# reading app

Local, page-grounded reading app for PDFs and course materials.

## What this app uses

- Python
- PyMuPDF for PDF rendering
- PaddleOCR for OCR on scanned pages
- LlamaIndex for document indexing and retrieval
- Ollama for local embeddings / local LLMs when available
- JSON files for local persistence

## Specification

### Input
- One PDF at a time.
- The app preserves page boundaries and page numbers.
- Each reading gets its own local folder under `data/ocr/<pdf-stem>/` by default.

### OCR layer
- Render PDF pages locally with PyMuPDF.
- OCR each page separately with PaddleOCR.
- Keep page text, OCR confidence, and source metadata.
- Save raw OCR output to disk.

### Indexing layer
- Create one LlamaIndex `Document` per page.
- Chunk from page documents, not from one big chapter blob.
- Preserve page number metadata in every node.
- Persist the index locally per reading.

### Retrieval mode
- Answer specific questions with top-k retrieval.
- Ground answers in retrieved pages only.
- Include page-number citations.
- Say when evidence is insufficient.

### Reading / summarization mode
- Summarize the whole chapter from all pages.
- Use page-level summaries, then merge upward.
- Do not rely on top-k retrieval for full-chapter summaries.
- Keep every claim tied to page citations.

### Verification
- Check that each factual claim has a citation.
- Remove unsupported or overstated claims.
- Keep the output auditable against the source PDF.

## How to run

Put a PDF in `data/raw/`, then run:

```bash
python ingest.py --file "Homer Iliad Book 1.pdf" --reading-id iliad_book1 --title "Homer Iliad Book 1" --author Homer --renderer pymupdf --dpi 120
```

You can also use a full path instead of a filename. If the file name is found in `data/raw/`, the app will use that automatically.

## Current project layout

```text
data/
  raw/
    Homer Iliad Book 1.pdf
  ocr/
    Homer Iliad Book 1/
      metadata.json
      pages.json
      source.pdf
      index/
```

## Current status

Implemented:
- OCR page extraction
- Local persistence of page text and metadata
- LlamaIndex ingestion and index persistence
- Smoke test on `Homer Iliad Book 1.pdf`

Next:
- Retrieval/Q&A tool
- Full-chapter hierarchical summarization
- Citation verifier
