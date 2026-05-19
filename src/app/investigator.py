from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from functools import lru_cache
import json
import math
import re
from pathlib import Path
from typing import Any

from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

from .models import OCRPage
from .persist import load_metadata, load_pages
from .pipeline import load_reading_index

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "could", "did", "do", "does",
    "for", "from", "had", "has", "have", "he", "her", "him", "his", "how", "i", "in", "is",
    "it", "its", "me", "my", "of", "on", "or", "our", "she", "that", "the", "their", "them",
    "there", "these", "they", "this", "those", "to", "was", "we", "were", "what", "when", "where",
    "which", "who", "why", "will", "with", "you", "your",
}

_ABSTRACT_MARKERS = (
    "why",
    "how",
    "irony",
    "theme",
    "significance",
    "motivation",
    "meaning",
    "purpose",
    "difference",
    "contrast",
    "compare",
)

_SUPPORT_MARKERS = {
    "because", "therefore", "however", "but", "yet", "although", "since", "so", "thus",
    "despite", "instead", "implies", "suggests", "shows", "reveals", "leads", "leaving",
    "thereby", "as a result", "in order to", "for this reason",
}

_BROAD_QUERY_MARKERS = (
    "trace",
    "chain",
    "evidence",
    "essay",
    "300-word",
    "500-word",
    "book 1",
    "how does",
    "what role",
)

_READING_CACHE: dict[tuple[str, str], dict[str, Any]] = {}
_ENTITY_PATTERN = re.compile(r"\b(?:[A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,3})\b")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*\]")
_CITED_PAGE_RE = re.compile(r"\[p\.\s*(\d+)\]")
_TRAILING_CITATION_RE = re.compile(r"\(p\.?\s*$", flags=re.I)
_LEADING_INDEX_RE = re.compile(r"^\s*\d+\]")


@dataclass(slots=True)
class RetrievedChunk:
    chunk_id: str
    page_number: int
    text: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EvidenceSnippet:
    page_number: int
    chunk_id: str
    quote: str
    score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InvestigationResult:
    reading_id: str
    question: str
    refined_query: str
    answer: str
    hits: list[RetrievedChunk]
    selected_evidence: list[EvidenceSnippet]
    answer_model: str | None = None
    diagnostics: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "reading_id": self.reading_id,
            "question": self.question,
            "refined_query": self.refined_query,
            "answer": self.answer,
            "answer_model": self.answer_model,
            "hits": [hit.to_dict() for hit in self.hits],
            "selected_evidence": [item.to_dict() for item in self.selected_evidence],
            "diagnostics": self.diagnostics or {},
        }


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


@lru_cache(maxsize=8192)
def _tokenize_cached(text: str) -> tuple[str, ...]:
    return tuple(token for token in re.findall(r"[A-Za-z0-9']+", text.lower()) if token and token not in _STOPWORDS)


def _tokenize(text: str) -> list[str]:
    return list(_tokenize_cached(text))


@lru_cache(maxsize=8192)
def _extract_entities_cached(text: str, limit: int = 12) -> tuple[str, ...]:
    pattern = re.compile(r"\b(?:[A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,3})\b")
    seen: set[str] = set()
    entities: list[str] = []
    for match in pattern.findall(text or ""):
        entity = re.sub(r"\s+", " ", match).strip(" ,.;:!?\"'")
        if len(entity) < 2:
            continue
        lower = entity.lower()
        if lower in _STOPWORDS or lower in seen:
            continue
        if any(word.lower() in _STOPWORDS for word in entity.split()):
            continue
        seen.add(lower)
        entities.append(entity)
        if len(entities) >= limit:
            break
    return tuple(entities)


def _extract_entities(text: str, limit: int = 12) -> list[str]:
    return list(_extract_entities_cached(text, limit))
    pattern = re.compile(r"\b(?:[A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,3})\b")
    seen: set[str] = set()
    entities: list[str] = []
    for match in pattern.findall(text or ""):
        entity = re.sub(r"\s+", " ", match).strip(" ,.;:!?\"'")
        if len(entity) < 2:
            continue
        lower = entity.lower()
        if lower in _STOPWORDS or lower in seen:
            continue
        if any(word.lower() in _STOPWORDS for word in entity.split()):
            continue
        seen.add(lower)
        entities.append(entity)
        if len(entities) >= limit:
            break
    return entities


def _load_summary_context(reading_id: str, base_dir: str | Path = "data/ocr") -> dict[str, Any]:
    summary_path = Path(base_dir) / reading_id / "summaries" / "summary.json"
    if not summary_path.exists():
        return {
            "merged_summary": None,
            "window_summaries": [],
            "summary_entities": [],
            "summary_keywords": [],
            "summary_relations": [],
        }
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        return {
            "merged_summary": data.get("merged_summary"),
            "window_summaries": data.get("windows", []),
            "summary_entities": data.get("summary_entities", []),
            "summary_keywords": data.get("summary_keywords", []),
            "summary_relations": data.get("summary_relations", []),
        }
    except Exception:
        return {
            "merged_summary": None,
            "window_summaries": [],
            "summary_entities": [],
            "summary_keywords": [],
            "summary_relations": [],
        }


def _get_reading_assets(reading_id: str, base_dir: str | Path = "data/ocr") -> dict[str, Any]:
    base = str(Path(base_dir).resolve())
    key = (base, reading_id)
    cached = _READING_CACHE.get(key)
    if cached is not None:
        return cached
    reading_dir = Path(base_dir) / reading_id
    summary_context = _load_summary_context(reading_id, base_dir)
    assets = {
        "metadata": load_metadata(reading_dir),
        "pages": [OCRPage(**page) for page in load_pages(reading_dir)],
        "summary_context": summary_context,
        "summary_signal_terms": _summary_signal_terms(summary_context),
    }
    try:
        assets["index"] = load_reading_index(reading_id, base_dir=base_dir)
    except Exception as exc:
        assets["index_error"] = f"{type(exc).__name__}: {exc}"
    _READING_CACHE[key] = assets
    return assets


def _summary_signal_terms(summary_context: dict[str, Any]) -> tuple[str, ...]:
    cached_terms = summary_context.get("summary_signal_terms")
    if isinstance(cached_terms, tuple):
        return cached_terms
    if isinstance(cached_terms, list):
        cached_tuple = tuple(cached_terms)
        summary_context["summary_signal_terms"] = cached_tuple
        return cached_tuple
    terms: list[str] = []
    seen: set[str] = set()
    for key in ("summary_entities", "summary_keywords", "summary_relations"):
        for item in summary_context.get(key, []) or []:
            for term in _tokenize(str(item)):
                if term not in seen:
                    seen.add(term)
                    terms.append(term)
    if terms:
        cached_tuple = tuple(terms)
        summary_context["summary_signal_terms"] = cached_tuple
        return cached_tuple

    texts: list[str] = []
    merged = summary_context.get("merged_summary")
    if merged:
        texts.append(str(merged))
    for window in summary_context.get("window_summaries", []) or []:
        if isinstance(window, dict):
            texts.append(str(window.get("text", "")))
    fallback_entities = []
    pattern = re.compile(r"\b(?:[A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,3})\b")
    for text in texts:
        for match in pattern.findall(text):
            for term in _tokenize(match):
                if term not in seen:
                    seen.add(term)
                    fallback_entities.append(term)
    cached_tuple = tuple(fallback_entities)
    summary_context["summary_signal_terms"] = cached_tuple
    return cached_tuple


def refine_query(question: str) -> str:
    text = _normalize(question)
    text = re.sub(r"^(can you|could you|would you|please|tell me|help me|i want to know)\s+", "", text, flags=re.I)
    text = re.sub(r"^(what|who|when|where|why|how|which) is\s+", "", text, flags=re.I)
    text = re.sub(r"^(what|who|when|where|why|how|which) are\s+", "", text, flags=re.I)
    text = text.rstrip("?!. ")
    return text or question.strip()


@lru_cache(maxsize=4096)
def _question_profile(question: str) -> dict[str, bool]:
    q = question.lower()
    return {
        "abstract": any(marker in q for marker in _ABSTRACT_MARKERS),
        "factual": any(q.startswith(prefix) for prefix in ("who ", "what ", "when ", "where ")),
        "comparative": any(word in q for word in ("compare", "difference", "similar", "contrast")),
    }


@lru_cache(maxsize=4096)
def _question_context(question: str) -> tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]]:
    refined = refine_query(question)
    tokens = _tokenize_cached(question)
    entities = tuple(_extract_entities(question))
    broad = any(marker in question.lower() for marker in _BROAD_QUERY_MARKERS) or len(tokens) >= 12
    return refined, tokens, entities, broad, _question_profile(question)


@lru_cache(maxsize=4096)
def _is_broad_question(question: str) -> bool:
    return _question_context(question)[3]


def _build_query_variants(question: str, summary_context: dict[str, Any], question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> list[str]:
    base, _, _, broad, profile = question_ctx or _question_context(question)
    entity_terms = summary_context.get("summary_entities", [])[:6]
    keyword_terms = summary_context.get("summary_keywords", [])[:8]
    relation_terms = summary_context.get("summary_relations", [])[:4]

    variants = [base]
    # Keep precise questions precise. Summary-derived terms are useful for broad
    # thematic/essay prompts, but they polluted named-entity factual questions.
    if broad and entity_terms:
        variants.append(_normalize(f"{base} {' '.join(entity_terms[:4])}"))
    if broad and keyword_terms:
        variants.append(_normalize(f"{base} {' '.join(keyword_terms[:5])}"))
    if broad and profile["comparative"] and relation_terms:
        variants.append(_normalize(f"{base} {' '.join(relation_terms[:2])}"))

    cleaned: list[str] = []
    seen: set[str] = set()
    for variant in variants:
        if not variant or variant in seen:
            continue
        seen.add(variant)
        cleaned.append(variant)
    return cleaned


def _page_chunks(page: OCRPage, chunk_size: int = 1024, chunk_overlap: int = 120) -> list[tuple[str, str]]:
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    document = Document(
        text=page.text,
        metadata={"page_number": page.page_number},
        doc_id=f"page_{page.page_number:04d}",
    )
    nodes = splitter.get_nodes_from_documents([document])
    chunks: list[tuple[str, str]] = []
    for index, node in enumerate(nodes, start=1):
        chunk_id = f"p{page.page_number:04d}_c{index:02d}"
        chunks.append((chunk_id, node.get_content()))
    return chunks


def _score_chunk(query_terms: list[str], query_phrase: str, chunk_text: str, doc_freqs: dict[str, int], total_chunks: int) -> float:
    tokens = _tokenize(chunk_text)
    if not tokens:
        return 0.0
    counts = Counter(tokens)
    score = 0.0
    for term in query_terms:
        if term not in counts:
            continue
        df = doc_freqs.get(term, 0)
        idf = math.log((total_chunks + 1) / (df + 1)) + 1.0
        tf = counts[term] / len(tokens)
        score += idf * tf * 10.0
    if query_phrase and query_phrase.lower() in chunk_text.lower():
        score += 2.5
    score += len(set(query_terms) & set(tokens)) * 0.25
    return score


def _retrieve_with_index(
    reading_id: str,
    query: str,
    base_dir: str | Path,
    top_k: int,
    diagnostics: dict[str, Any] | None = None,
) -> list[RetrievedChunk]:
    try:
        assets = _get_reading_assets(reading_id, base_dir)
        metadata = assets["metadata"]
        if metadata.get("embedding_backend") == "mock":
            if diagnostics is not None:
                diagnostics["vector_skipped_reason"] = "metadata embedding_backend is mock"
            return []
        index = assets.get("index")
        if index is None:
            if diagnostics is not None:
                diagnostics["vector_attempted"] = True
                diagnostics["vector_succeeded"] = False
                diagnostics["vector_error"] = assets.get("index_error", "index unavailable")
            return []
        retriever = index.as_retriever(similarity_top_k=top_k)
        results = retriever.retrieve(query)
        hits: list[RetrievedChunk] = []
        for result in results:
            node = result.node
            page_number = int(node.metadata.get("page_number", 0))
            chunk_id = str(node.metadata.get("chunk_id", f"p{page_number:04d}"))
            hits.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    page_number=page_number,
                    text=node.get_content(),
                    score=float(result.score or 0.0),
                )
            )
        hits.sort(key=lambda item: (-item.score, item.page_number, item.chunk_id))
        if diagnostics is not None:
            diagnostics["vector_attempted"] = True
            diagnostics["vector_succeeded"] = True
        return hits[:top_k]
    except Exception as exc:
        if diagnostics is not None:
            diagnostics["vector_attempted"] = True
            diagnostics["vector_succeeded"] = False
            diagnostics["vector_error"] = f"{type(exc).__name__}: {exc}"
        return []


def retrieve_chunks(
    reading_id: str,
    question: str,
    base_dir: str | Path = "data/ocr",
    top_k: int = 10,
    summary_context: dict[str, Any] | None = None,
    diagnostics: dict[str, Any] | None = None,
    question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None,
) -> list[RetrievedChunk]:
    summary_context = summary_context or _get_reading_assets(reading_id, base_dir)["summary_context"]
    variants = _build_query_variants(question, summary_context, question_ctx=question_ctx)
    if diagnostics is not None:
        diagnostics["query_variants"] = variants
        diagnostics.setdefault("vector_attempted", False)
        diagnostics.setdefault("vector_succeeded", False)
    dedup: dict[tuple[int, str], RetrievedChunk] = {}

    for query in variants:
        index_hits = _retrieve_with_index(reading_id, query, base_dir, top_k, diagnostics=diagnostics)
        for hit in index_hits:
            key = (hit.page_number, hit.chunk_id)
            existing = dedup.get(key)
            if existing is None or hit.score > existing.score:
                dedup[key] = hit

    if dedup:
        hits = sorted(dedup.values(), key=lambda item: (-item.score, item.page_number, item.chunk_id))
        if diagnostics is not None:
            diagnostics["retrieval_backend"] = "vector"
            diagnostics["initial_pages"] = [hit.page_number for hit in hits[:top_k]]
        return hits[:top_k]

    pages = _get_reading_assets(reading_id, base_dir)["pages"]
    query_terms = _tokenize(variants[0]) or _tokenize(question)

    chunks: list[tuple[str, int, str]] = []
    for page in pages:
        for chunk_id, text in _page_chunks(page):
            chunks.append((chunk_id, page.page_number, text))

    doc_freqs: dict[str, int] = {}
    for term in set(query_terms):
        doc_freqs[term] = sum(1 for _, _, text in chunks if term in _tokenize(text))

    scored: list[RetrievedChunk] = []
    for chunk_id, page_number, text in chunks:
        score = _score_chunk(query_terms, question, text, doc_freqs, len(chunks))
        if score <= 0:
            continue
        scored.append(RetrievedChunk(chunk_id=chunk_id, page_number=page_number, text=text, score=score))

    scored.sort(key=lambda item: (-item.score, item.page_number, item.chunk_id))
    if diagnostics is not None:
        diagnostics["retrieval_backend"] = "lexical_fallback"
        diagnostics["initial_pages"] = [hit.page_number for hit in scored[:top_k]]
    return scored[:top_k]


def _rerank_hits_for_question(question: str, hits: list[RetrievedChunk], summary_context: dict[str, Any] | None = None, question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> list[RetrievedChunk]:
    summary_context = summary_context or {}
    _, qtokens, _, broad, _ = question_ctx or _question_context(question)
    summary_terms = set(_summary_signal_terms(summary_context)) if broad else set()
    qterms = set(qtokens)
    weighted: list[tuple[float, RetrievedChunk]] = []

    for hit in hits:
        tokens = set(_tokenize(hit.text))
        score = hit.score

        # Keep reranking lightweight: prefer direct question-term overlap and,
        # only for broad prompts, document-specific summary signals. Avoid generic
        # discourse markers such as "because/however"; they made retrieval too lexical.
        score += len(tokens & qterms) * 0.35
        score += len(tokens & summary_terms) * 0.15

        weighted.append((score, hit))

    weighted.sort(key=lambda item: (-item[0], item[1].page_number, item[1].chunk_id))
    return [hit for _, hit in weighted]


def _expand_with_adjacent_pages(
    reading_id: str,
    hits: list[RetrievedChunk],
    base_dir: str | Path,
    max_seed_pages: int = 4,
) -> list[RetrievedChunk]:
    if not hits:
        return hits
    try:
        pages = _get_reading_assets(reading_id, base_dir)["pages"]
    except Exception:
        return hits

    by_page = {page.page_number: page for page in pages}
    dedup: dict[tuple[int, str], RetrievedChunk] = {(hit.page_number, hit.chunk_id): hit for hit in hits}
    seed_pages = [hit.page_number for hit in hits[:max_seed_pages]]
    seed_score = hits[0].score if hits else 1.0
    for page_number in seed_pages:
        page = by_page.get(page_number)
        if page is not None:
            chunk_id = f"p{page_number:04d}_full"
            key = (page_number, chunk_id)
            if key not in dedup:
                dedup[key] = RetrievedChunk(
                    chunk_id=chunk_id,
                    page_number=page_number,
                    text=page.text,
                    score=seed_score * 1.05,
                )
        for adjacent in (page_number - 1, page_number + 1):
            page = by_page.get(adjacent)
            if page is None:
                continue
            chunk_id = f"p{adjacent:04d}_adjacent"
            key = (adjacent, chunk_id)
            if key in dedup:
                continue
            dedup[key] = RetrievedChunk(
                chunk_id=chunk_id,
                page_number=adjacent,
                text=page.text,
                score=seed_score * 0.72,
            )
    return list(dedup.values())


@lru_cache(maxsize=8192)
def _split_sentences_cached(text: str) -> tuple[str, ...]:
    pieces = re.split(r"(?<=[.!?])\s+", _normalize(text))
    return tuple(piece.strip() for piece in pieces if piece.strip())


def _split_sentences(text: str) -> list[str]:
    return list(_split_sentences_cached(text))


def _sentence_window(sentences: list[str], center_index: int, radius: int = 1) -> str:
    start = max(0, center_index - radius)
    end = min(len(sentences), center_index + radius + 1)
    return " ".join(sentences[start:end]).strip()


@lru_cache(maxsize=16384)
def _best_sentence_score_cached(sentence: str, question: str, broad: bool, summary_terms: tuple[str, ...]) -> float:
    qterms = set(_tokenize(question))
    stokens = set(_tokenize(sentence))
    sterms = set(summary_terms) if broad else set()
    score = len(qterms & stokens) * 1.25
    score += len(stokens & sterms) * 0.15
    return score


def _best_sentence_score(sentence: str, question: str, summary_context: dict[str, Any] | None = None, question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> float:
    summary_context = summary_context or {}
    _, _, _, broad, _ = question_ctx or _question_context(question)
    summary_terms = tuple(_summary_signal_terms(summary_context)) if broad else tuple()
    return _best_sentence_score_cached(sentence, question, broad, summary_terms)


def _select_evidence_snippets(question: str, hits: list[RetrievedChunk], summary_context: dict[str, Any] | None = None, max_snippets: int = 3, question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> list[EvidenceSnippet]:
    profile = (question_ctx or _question_context(question))[4]
    weighted: list[tuple[float, EvidenceSnippet]] = []
    full_pages = {hit.page_number for hit in hits if hit.chunk_id.endswith("_full")}
    preferred_hits = [hit for hit in hits if hit.page_number not in full_pages or hit.chunk_id.endswith("_full")]
    for hit in preferred_hits:
        sentences = _split_sentences(hit.text)
        if not sentences:
            continue
        best_sentence = ""
        best_score = -1.0
        best_index = 0
        for index, sentence in enumerate(sentences):
            score = _best_sentence_score(sentence, question, summary_context=summary_context, question_ctx=question_ctx)
            if score > best_score:
                best_score = score
                best_sentence = sentence.strip()
                best_index = index
        if best_sentence:
            # Keep nearby context. Single-sentence extraction often stopped right
            # before the answer-bearing clause in dialogue-heavy texts.
            quote = _sentence_window(sentences, best_index, radius=3 if hit.chunk_id.endswith("_full") else 1)
            combined = hit.score + best_score
            weighted.append((combined, EvidenceSnippet(page_number=hit.page_number, chunk_id=hit.chunk_id, quote=quote, score=combined)))

    weighted.sort(key=lambda item: (-item[0], item[1].page_number, item[1].chunk_id))
    if not weighted:
        return []

    top_score = weighted[0][0]
    if profile["abstract"] or profile["comparative"] or _is_broad_question(question):
        cutoff = max(1.0, top_score * 0.45)
        max_snippets = max(max_snippets, 5)
    else:
        cutoff = max(0.6, top_score * 0.45)

    selected: list[EvidenceSnippet] = []
    seen: set[tuple[int, str]] = set()
    for score, snippet in weighted:
        if score < cutoff:
            continue
        key = (snippet.page_number, snippet.quote)
        if key in seen:
            continue
        seen.add(key)
        selected.append(snippet)
        if len(selected) >= max_snippets:
            break
    if not selected:
        selected.append(weighted[0][1])
    return selected


def _extract_cited_pages(text: str) -> set[int]:
    return {int(match.group(1)) for match in re.finditer(r"\[p\.\s*(\d+)\]", text)}


def _answer_entities(text: str) -> set[str]:
    return {entity.lower() for entity in _extract_entities(text)}


def _evidence_focus_terms(question: str, selected_evidence: list[EvidenceSnippet], summary_context: dict[str, Any] | None = None, question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> list[str]:
    refined, qtokens, qentities, broad, _ = question_ctx or _question_context(question)
    qterms = set(qtokens)
    terms: list[str] = []
    seen: set[str] = set()

    def add(term: str) -> None:
        cleaned = _normalize(term)
        if not cleaned:
            return
        lower = cleaned.lower()
        if lower in seen or lower in _STOPWORDS:
            return
        seen.add(lower)
        terms.append(cleaned)

    for entity in qentities[:3]:
        add(entity)
    for token in qtokens:
        if len(token) > 3:
            add(token)
    for snippet in selected_evidence:
        for entity in _extract_entities(snippet.quote):
            if entity.lower() not in {item.lower() for item in qentities}:
                add(entity)
        for token in _tokenize(snippet.quote):
            if len(token) > 4 and token not in qterms:
                add(token)
        if len(terms) >= 8:
            break
    if broad:
        for signal in _summary_signal_terms(summary_context or {}):
            if len(signal) > 3:
                add(signal)
            if len(terms) >= 10:
                break
    if refined and refined.lower() not in seen:
        terms.insert(0, refined)
    return terms[:10]


def _plan_followup_queries(
    question: str,
    selected_evidence: list[EvidenceSnippet],
    summary_context: dict[str, Any] | None = None,
    question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None,
) -> list[str]:
    base, qtokens, qentities, broad, profile = question_ctx or _question_context(question)
    focus_terms = _evidence_focus_terms(question, selected_evidence, summary_context=summary_context, question_ctx=question_ctx)
    queries: list[str] = []
    seen: set[str] = set()

    def add(query: str) -> None:
        cleaned = _normalize(query)
        if not cleaned or cleaned.lower() in seen:
            return
        seen.add(cleaned.lower())
        queries.append(cleaned)

    add(base)

    if qentities and focus_terms:
        add(_normalize(f"{qentities[0]} {' '.join(focus_terms[:3])}"))

    if focus_terms and any(term.lower() not in {entity.lower() for entity in qentities} for term in focus_terms[1:4]):
        add(_normalize(" ".join(focus_terms[:4])))

    if broad or profile["abstract"] or profile["comparative"]:
        add(_normalize(f"{base} {' '.join(focus_terms[:5])}"))

    return queries[:2]


def _answer_from_citations(question: str, selected_evidence: list[EvidenceSnippet], question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> str:
    if not selected_evidence:
        return "I couldn’t find enough evidence in the retrieved pages."
    _, _, _, broad, profile = question_ctx or _question_context(question)
    answered: list[str] = []
    seen_pages: set[int] = set()

    for snippet in selected_evidence:
        if snippet.page_number in seen_pages:
            continue
        seen_pages.add(snippet.page_number)
        sentences = _split_sentences(snippet.quote)
        if not sentences:
            continue
        best = max(sentences, key=lambda sent: (_best_sentence_score(sent, question, question_ctx=question_ctx), _sentence_support(sent, [snippet])))
        best = _normalize(best)
        if not best:
            continue
        if best[-1] not in ".!?":
            best += "."
        answered.append(f"{best} [p. {snippet.page_number}]")
        if len(answered) >= (2 if broad or profile["abstract"] or profile["comparative"] else 1):
            break

    if not answered:
        snippets = []
        for snippet in selected_evidence[:3]:
            quote = _normalize(snippet.quote)
            if len(quote) > 180:
                quote = quote[:180].rstrip() + "..."
            snippets.append(f"[p. {snippet.page_number}] {quote}")
        return "Based on the evidence, " + " ".join(snippets)

    if broad or profile["abstract"] or profile["comparative"]:
        return "Based on the evidence, " + " ".join(answered)
    return answered[0]


@lru_cache(maxsize=16384)
def _sentence_support_cached(sentence: str, quote: str) -> float:
    sent_terms = set(_tokenize(sentence))
    if not sent_terms:
        return 0.0
    quote_terms = set(_tokenize(quote))
    overlap = len(sent_terms & quote_terms)
    if overlap == 0:
        return 0.0
    ratio = overlap / max(1, len(sent_terms))
    phrase_hit = 1.0 if sentence.lower() in quote.lower() or quote.lower() in sentence.lower() else 0.0
    return ratio + phrase_hit


def _sentence_support(sentence: str, evidence: list[EvidenceSnippet]) -> float:
    best = 0.0
    for snippet in evidence:
        best = max(best, _sentence_support_cached(sentence, snippet.quote))
    return best


def _validate_llm_answer(answer: str, question: str, evidence: list[EvidenceSnippet], question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> str | None:
    cleaned = _normalize(answer)
    if not cleaned:
        return None
    if re.search(r"\(p\.?\s*$", cleaned, flags=re.I):
        return None
    if re.match(r"^\s*\d+\]", cleaned):
        return None
    evidence_pages = {snippet.page_number for snippet in evidence}
    evidence_entities = _answer_entities(" ".join(snippet.quote for snippet in evidence))
    _, _, question_entities_raw, _, _ = question_ctx or _question_context(question)
    question_entities = {entity.lower() for entity in question_entities_raw}
    supported: list[str] = []
    for sentence in _split_sentences(cleaned):
        if re.match(r"^\s*\d+\]", sentence):
            continue
        support = _sentence_support(sentence, evidence)
        cited_pages = _extract_cited_pages(sentence)
        if cited_pages and not cited_pages.issubset(evidence_pages):
            continue
        sentence_entities = _answer_entities(sentence)
        unsupported_entities = sentence_entities - evidence_entities - question_entities
        if unsupported_entities:
            continue
        if support >= 0.4:
            supported.append(sentence)
    return " ".join(supported).strip() if supported else None


def _filter_supported_answer(answer: str, question: str, evidence: list[EvidenceSnippet], question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> str:
    validated = _validate_llm_answer(answer, question, evidence, question_ctx=question_ctx)
    return validated or ""


def _fallback_answer(question: str, selected_evidence: list[EvidenceSnippet], question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> str:
    if not selected_evidence:
        return "I couldn’t find enough evidence in the retrieved pages."
    sentences: list[str] = []
    seen_pages: set[int] = set()
    _, _, _, broad, _ = question_ctx or _question_context(question)
    for snippet in selected_evidence:
        if snippet.page_number in seen_pages:
            continue
        seen_pages.add(snippet.page_number)
        parts = _split_sentences(snippet.quote)
        if not parts:
            continue
        best = max(parts, key=lambda sent: (_best_sentence_score(sent, question, question_ctx=question_ctx), _sentence_support(sent, [snippet])))
        best = _normalize(best)
        if best and best not in sentences:
            sentences.append(f"{best} [p. {snippet.page_number}]")
        if len(sentences) >= 2:
            break
    if not sentences:
        snippets = []
        for snippet in selected_evidence[:3]:
            quote = _normalize(snippet.quote)
            if len(quote) > 180:
                quote = quote[:180].rstrip() + "..."
            snippets.append(f"[p. {snippet.page_number}] {quote}")
        return "Based on the evidence, " + " ".join(snippets)
    if broad:
        return "Based on the evidence, " + " ".join(sentences)
    return " ".join(sentences)


def _evidence_sufficiency(question: str, evidence: list[EvidenceSnippet], question_ctx: tuple[str, tuple[str, ...], tuple[str, ...], bool, dict[str, bool]] | None = None) -> dict[str, Any]:
    _, qtokens, question_entities_raw, broad, _ = question_ctx or _question_context(question)
    qterms = set(qtokens)
    evidence_text = " ".join(snippet.quote for snippet in evidence)
    evidence_terms = set(_tokenize(evidence_text))
    cited_pages = sorted({snippet.page_number for snippet in evidence})
    overlap = sorted(qterms & evidence_terms)
    question_entities = {entity.lower() for entity in question_entities_raw}
    evidence_entities = {entity.lower() for entity in _extract_entities(evidence_text)}
    entity_overlap = sorted(question_entities & evidence_entities)
    support_hits = [marker for marker in _SUPPORT_MARKERS if marker in evidence_text.lower()]
    min_pages = 3 if broad else 1
    min_overlap = 2 if broad else min(2, len(qterms)) if qterms else 0
    sufficient = bool(evidence) and len(cited_pages) >= min_pages and (len(overlap) >= min_overlap or len(entity_overlap) >= 1)
    if broad:
        sufficient = sufficient and (len(support_hits) >= 1 or len(overlap) >= 2 or len(entity_overlap) >= 2)
    return {
        "sufficient": sufficient,
        "broad_question": broad,
        "cited_pages": cited_pages,
        "question_term_overlap": overlap,
        "entity_overlap": entity_overlap,
        "support_hits": support_hits[:5],
        "reason": "ok" if sufficient else "too few pages, weak entity coverage, or weak support markers",
    }


def investigate_reading(
    reading_id: str,
    question: str,
    base_dir: str | Path = "data/ocr",
    top_k: int = 10,
) -> InvestigationResult:
    summary_context = _load_summary_context(reading_id, base_dir)
    question_ctx = _question_context(question)
    refined_query = question_ctx[0]
    diagnostics: dict[str, Any] = {
        "citation_only_mode": True,
    }
    hits = retrieve_chunks(
        reading_id,
        question,
        base_dir=base_dir,
        top_k=max(top_k, 12 if question_ctx[3] else top_k),
        summary_context=summary_context,
        diagnostics=diagnostics,
        question_ctx=question_ctx,
    )
    diagnostics["pages_before_rerank"] = [hit.page_number for hit in hits]
    hits = _rerank_hits_for_question(question, hits, summary_context=summary_context, question_ctx=question_ctx)
    diagnostics["pages_after_rerank"] = [hit.page_number for hit in hits[:top_k]]

    expanded_hits = _expand_with_adjacent_pages(reading_id, hits[:top_k], base_dir)
    if len(expanded_hits) > len(hits[:top_k]):
        diagnostics["adjacent_expansion_added"] = len(expanded_hits) - len(hits[:top_k])
        hits = _rerank_hits_for_question(question, expanded_hits, summary_context=summary_context, question_ctx=question_ctx)
    else:
        hits = hits[:top_k]
    diagnostics["pages_after_expansion"] = [hit.page_number for hit in hits[: max(top_k, 12)]]

    selected_evidence = _select_evidence_snippets(
        question,
        hits[: max(top_k, 12 if question_ctx[3] else top_k)],
        summary_context=summary_context,
        max_snippets=5 if question_ctx[3] else 3,
        question_ctx=question_ctx,
    )
    diagnostics["evidence_sufficiency"] = _evidence_sufficiency(question, selected_evidence, question_ctx=question_ctx)

    followup_round = 0
    while followup_round < 2:
        sufficiency = _evidence_sufficiency(question, selected_evidence, question_ctx=question_ctx)
        if sufficiency["sufficient"]:
            diagnostics["evidence_sufficiency_after_followup"] = sufficiency
            break
        followup_queries = _plan_followup_queries(question, selected_evidence, summary_context=summary_context, question_ctx=question_ctx)
        if not followup_queries:
            diagnostics["followup_queries"] = [] if followup_round == 0 else diagnostics.get("followup_queries")
            diagnostics["evidence_sufficiency_after_followup"] = sufficiency
            break
        diagnostics.setdefault("followup_queries", [])
        diagnostics["followup_queries"] = list(dict.fromkeys((diagnostics["followup_queries"] or []) + followup_queries))
        merged: dict[tuple[int, str], RetrievedChunk] = {(hit.page_number, hit.chunk_id): hit for hit in hits}
        new_hit_count = 0
        for followup in followup_queries:
            followup_hits = retrieve_chunks(
                reading_id,
                followup,
                base_dir=base_dir,
                top_k=6,
                summary_context=summary_context,
            )
            for hit in followup_hits:
                key = (hit.page_number, hit.chunk_id)
                existing = merged.get(key)
                if existing is None or hit.score > existing.score:
                    merged[key] = hit
                    new_hit_count += 1
        if new_hit_count == 0:
            diagnostics["evidence_sufficiency_after_followup"] = sufficiency
            break
        hits = _rerank_hits_for_question(question, list(merged.values()), summary_context=summary_context, question_ctx=question_ctx)
        hits = _rerank_hits_for_question(question, _expand_with_adjacent_pages(reading_id, hits[: max(top_k, 12)], base_dir), summary_context=summary_context, question_ctx=question_ctx)
        selected_evidence = _select_evidence_snippets(
            question,
            hits[: max(top_k, 12 if question_ctx[3] else top_k)],
            summary_context=summary_context,
            max_snippets=5 if question_ctx[3] else 3,
            question_ctx=question_ctx,
        )
        diagnostics["pages_after_followup"] = [hit.page_number for hit in hits[: max(top_k, 12)]]
        diagnostics["evidence_sufficiency_after_followup"] = _evidence_sufficiency(question, selected_evidence, question_ctx=question_ctx)
        followup_round += 1

    answer = _answer_from_citations(question, selected_evidence, question_ctx=question_ctx)
    return InvestigationResult(
        reading_id=reading_id,
        question=question,
        refined_query=refined_query,
        answer=answer,
        hits=hits[:top_k],
        selected_evidence=selected_evidence,
        diagnostics=diagnostics,
    )


def investigation_markdown(result: InvestigationResult) -> str:
    lines = [
        f"Question: {result.question}",
        f"Response: {result.answer}",
        "Evidence:",
    ]
    for snippet in result.selected_evidence:
        quote = _normalize(snippet.quote)
        if len(quote) > 1000:
            quote = quote[:1000].rstrip() + "..."
        lines.append(f"- [p. {snippet.page_number} | {snippet.chunk_id}] {quote}")
    if result.diagnostics:
        lines.extend([
            "Diagnostics:",
            f"- citation_only_mode: {result.diagnostics.get('citation_only_mode')}",
            f"- retrieval_backend: {result.diagnostics.get('retrieval_backend')}",
            f"- vector_succeeded: {result.diagnostics.get('vector_succeeded')}",
            f"- pages_before_rerank: {result.diagnostics.get('pages_before_rerank')}",
            f"- pages_after_expansion: {result.diagnostics.get('pages_after_expansion')}",
            f"- followup_queries: {result.diagnostics.get('followup_queries')}",
            f"- pages_after_followup: {result.diagnostics.get('pages_after_followup')}",
            f"- evidence_sufficiency: {result.diagnostics.get('evidence_sufficiency_after_followup') or result.diagnostics.get('evidence_sufficiency')}",
        ])
    return "\n".join(lines).strip() + "\n"
