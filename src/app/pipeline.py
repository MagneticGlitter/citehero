from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from llama_index.core import Document, Settings, StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.embeddings.mock_embed_model import MockEmbedding
from llama_index.core.node_parser import SentenceSplitter

from .models import OCRPage, ReadingMetadata
from .ocr import ocr_pdf_by_page
from .persist import copy_source_pdf, default_reading_id_from_path, ensure_reading_dir, load_metadata, resolve_source_pdf, save_metadata


def _configure_embeddings(embedding_backend: str, ollama_base_url: str, embed_model: str) -> str:
    if embedding_backend == "mock":
        Settings.embed_model = MockEmbedding(embed_dim=1536)
        return "mock"

    try:
        import httpx

        httpx.get(f"{ollama_base_url.rstrip('/')}/api/tags", timeout=1.0)
        from llama_index.embeddings.ollama import OllamaEmbedding

        Settings.embed_model = OllamaEmbedding(model_name=embed_model, base_url=ollama_base_url)
        return "ollama"
    except Exception:
        Settings.embed_model = MockEmbedding(embed_dim=1536)
        return "mock"


def _configure_llm(ollama_base_url: str, llm_model: str | None) -> str | None:
    if not llm_model:
        return None
    try:
        from llama_index.llms.ollama import Ollama

        Settings.llm = Ollama(model=llm_model, base_url=ollama_base_url)
        return llm_model
    except Exception:
        return None


def _document_for_page(page: OCRPage, metadata: ReadingMetadata) -> Document:
    doc_metadata = {
        "reading_id": metadata.reading_id,
        "title": metadata.title,
        "author": metadata.author,
        "course": metadata.course,
        "lecture": metadata.lecture,
        "page_number": page.page_number,
        "ocr_engine": page.ocr_engine,
        "source_path": page.source_path,
    }
    return Document(text=page.text, metadata=doc_metadata, doc_id=f"{metadata.reading_id}_p{page.page_number:04d}")


def _nodes_from_document(document: Document, reading_id: str, splitter: SentenceSplitter) -> list:
    nodes: list = []
    page_nodes = splitter.get_nodes_from_documents([document])
    page_number = int(document.metadata["page_number"])
    for chunk_index, node in enumerate(page_nodes, start=1):
        node.metadata.update(document.metadata)
        node.metadata["chunk_id"] = f"{reading_id}_p{page_number:04d}_c{chunk_index:02d}"
        node.metadata["page_number"] = page_number
        node.metadata["reading_id"] = reading_id
        nodes.append(node)
    return nodes


def load_reading_index(
    reading_id: str,
    base_dir: str | Path = "data/ocr",
    ollama_base_url: str = "http://localhost:11434",
    embed_model: str = "nomic-embed-text",
):
    reading_dir = Path(base_dir) / reading_id
    metadata = load_metadata(reading_dir)
    backend = metadata.get("embedding_backend", "mock")
    _configure_embeddings(backend, ollama_base_url, metadata.get("embed_model", embed_model))
    index_dir = reading_dir / "index"
    return load_index_from_storage(StorageContext.from_defaults(persist_dir=str(index_dir)))


def ingest_reading(
    file_path: str | Path,
    title: str,
    reading_id: str | None = None,
    author: str | None = None,
    course: str | None = None,
    lecture: str | None = None,
    base_dir: str | Path = "data/ocr",
    dpi: int = 200,
    lang: str = "en",
    renderer: str = "auto",
    embedding_backend: str = "auto",
    ollama_base_url: str = "http://localhost:11434",
    embed_model: str = "nomic-embed-text",
) -> Path:
    file_path = resolve_source_pdf(file_path)
    reading_id = reading_id or default_reading_id_from_path(file_path)
    reading_dir = ensure_reading_dir(base_dir, reading_id)

    metadata = ReadingMetadata(
        reading_id=reading_id,
        title=title,
        author=author,
        course=course,
        lecture=lecture,
        source_path=str(file_path),
        created_at=datetime.now(timezone.utc).isoformat(),
        dpi=dpi,
        ocr_engine="paddleocr",
        renderer="pymupdf",
        embedding_backend=embedding_backend,
        embed_model=embed_model,
    )

    copy_source_pdf(file_path, reading_dir)

    effective_embedding_backend = _configure_embeddings(embedding_backend, ollama_base_url, embed_model)
    metadata.embedding_backend = effective_embedding_backend
    save_metadata(reading_dir, metadata)

    splitter = SentenceSplitter(chunk_size=1024, chunk_overlap=120)
    index_dir = reading_dir / "index"
    storage_context = StorageContext.from_defaults()
    index = VectorStoreIndex(nodes=[], storage_context=storage_context)

    pages_path = reading_dir / "pages.json"
    pages_tmp_path = reading_dir / "pages.json.tmp"
    pages: list[OCRPage] = []
    page_count = 0
    with pages_tmp_path.open("w", encoding="utf-8") as handle:
        handle.write("[\n")
        first = True
        for page in ocr_pdf_by_page(file_path, reading_id=reading_id, title=title, author=author, dpi=dpi, lang=lang, renderer=renderer):
            if not first:
                handle.write(",\n")
            json.dump(page.to_dict(), handle, ensure_ascii=False)
            pages.append(page)
            document = _document_for_page(page, metadata)
            nodes = _nodes_from_document(document, reading_id=reading_id, splitter=splitter)
            index.insert_nodes(nodes)
            page_count += 1
            first = False
        handle.write("\n]\n")

    if page_count == 0:
        pages_tmp_path.unlink(missing_ok=True)
        raise RuntimeError("no pages were extracted from the PDF")

    pages_tmp_path.replace(pages_path)
    index.storage_context.persist(persist_dir=str(index_dir))

    reloaded = load_index_from_storage(StorageContext.from_defaults(persist_dir=str(index_dir)))
    if len(reloaded.storage_context.docstore.docs) != len(index.storage_context.docstore.docs):
        raise RuntimeError("index persistence check failed")

    return reading_dir
