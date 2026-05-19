from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
import json
import re

from llama_index.core import Settings

from .models import OCRPage, ReadingMetadata
from .persist import load_metadata, load_pages, save_metadata


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "could", "did", "do", "does",
    "for", "from", "had", "has", "have", "he", "her", "him", "his", "how", "i", "in", "is",
    "it", "its", "me", "my", "of", "on", "or", "our", "she", "that", "the", "their", "them",
    "there", "these", "they", "this", "those", "to", "was", "we", "were", "what", "when", "where",
    "which", "who", "why", "will", "with", "you", "your",
}


@dataclass(slots=True)
class PageWindowSummary:
    window_index: int
    page_start: int
    page_end: int
    page_numbers: list[int]
    text: str
    word_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReadingSummary:
    reading_id: str
    title: str
    window_size: int
    window_target_words: int
    window_hard_cap_words: int
    merge_target_words: int
    merge_hard_cap_words: int
    llm_model: str | None
    windows: list[PageWindowSummary] = field(default_factory=list)
    merged_summary: str | None = None
    summary_entities: list[str] = field(default_factory=list)
    summary_keywords: list[str] = field(default_factory=list)
    summary_relations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "reading_id": self.reading_id,
            "title": self.title,
            "window_size": self.window_size,
            "window_target_words": self.window_target_words,
            "window_hard_cap_words": self.window_hard_cap_words,
            "merge_target_words": self.merge_target_words,
            "merge_hard_cap_words": self.merge_hard_cap_words,
            "llm_model": self.llm_model,
            "windows": [window.to_dict() for window in self.windows],
            "merged_summary": self.merged_summary,
            "summary_entities": self.summary_entities,
            "summary_keywords": self.summary_keywords,
            "summary_relations": self.summary_relations,
        }


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _trim_words(text: str, max_words: int | None) -> str:
    if not text or max_words is None or max_words <= 0:
        return text.strip()
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def _group_pages(pages: Iterable[OCRPage], window_size: int) -> list[list[OCRPage]]:
    ordered = sorted(pages, key=lambda page: page.page_number)
    return [ordered[index : index + window_size] for index in range(0, len(ordered), window_size)]


def _format_window_source(window: list[OCRPage]) -> str:
    parts: list[str] = []
    for page in window:
        parts.append(f"[Page {page.page_number}]\n{page.text.strip()}")
    return "\n\n".join(parts).strip()


def _extract_entities(texts: Iterable[str], limit: int = 20) -> list[str]:
    pattern = re.compile(r"\b(?:[A-Z][A-Za-z'’-]*(?:\s+[A-Z][A-Za-z'’-]*){0,3})\b")
    seen: set[str] = set()
    entities: list[str] = []
    for text in texts:
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
                return entities
    return entities


def _extract_keywords(texts: Iterable[str], limit: int = 20) -> list[str]:
    counts: Counter[str] = Counter()
    for text in texts:
        for token in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower() if text else ""):
            if token in _STOPWORDS:
                continue
            counts[token] += 1
    return [word for word, _ in counts.most_common(limit)]


def _extract_relation_phrases(texts: Iterable[str], limit: int = 12) -> list[str]:
    markers = ("because", "therefore", "however", "but", "yet", "although", "so", "since", "despite", "until", "thus", "as a result", "in order to")
    phrases: list[str] = []
    seen: set[str] = set()
    for text in texts:
        for sentence in re.split(r"(?<=[.!?])\s+", text or ""):
            lowered = sentence.lower()
            if any(marker in lowered for marker in markers):
                cleaned = re.sub(r"\s+", " ", sentence).strip()
                key = cleaned.lower()
                if key not in seen:
                    seen.add(key)
                    phrases.append(cleaned)
                    if len(phrases) >= limit:
                        return phrases
    return phrases


def _complete(prompt: str) -> str:
    llm = Settings.llm
    if llm is None:
        raise RuntimeError("summary generation requires an LLM; pass --llm-model or configure Settings.llm")
    response = llm.complete(prompt)
    text = getattr(response, "text", None)
    if text is None:
        text = str(response)
    return text.strip()


def summarize_window(
    title: str,
    reading_id: str,
    window_index: int,
    window: list[OCRPage],
    target_words: int,
    hard_cap_words: int,
) -> PageWindowSummary:
    page_numbers = [page.page_number for page in window]
    page_start = page_numbers[0]
    page_end = page_numbers[-1]
    source = _format_window_source(window)
    prompt = (
        f"You are summarizing pages from the reading '{title}' ({reading_id}).\n"
        "Use only the OCR text below. Do not guess or invent details.\n"
        f"Return a grounded summary of pages {page_start}-{page_end}.\n"
        f"Target length: about {target_words} words.\n"
        f"Hard cap: {hard_cap_words} words.\n"
        "Prefer concise, factual prose and preserve useful names, events, objects, and relations.\n\n"
        f"OCR pages:\n{source}"
    )
    text = _trim_words(_complete(prompt), hard_cap_words)
    return PageWindowSummary(
        window_index=window_index,
        page_start=page_start,
        page_end=page_end,
        page_numbers=page_numbers,
        text=text,
        word_count=_word_count(text),
    )


def merge_window_summaries(
    title: str,
    reading_id: str,
    windows: list[PageWindowSummary],
    target_words: int,
    hard_cap_words: int,
) -> str:
    prompt_lines = []
    for window in windows:
        prompt_lines.append(f"[Pages {window.page_start}-{window.page_end}]\n{window.text}")
    prompt = (
        f"You are producing a document-level summary for '{title}' ({reading_id}).\n"
        "Use only the window summaries below. Do not add unsupported claims.\n"
        "Organize the answer with these sections:\n"
        "- who / what / when / why / how\n"
        "- story flow\n"
        "- relations\n"
        "- environments / objects / symbolism\n"
        "- mental model\n"
        "- interpretation\n"
        f"Target length: about {target_words} words.\n"
        f"Hard cap: {hard_cap_words} words total.\n\n"
        + "\n\n".join(prompt_lines)
    )
    return _trim_words(_complete(prompt), hard_cap_words)


def _derive_summary_signals(windows: list[PageWindowSummary], merged_summary: str | None) -> dict[str, list[str]]:
    texts = [window.text for window in windows]
    if merged_summary:
        texts.append(merged_summary)
    return {
        "summary_entities": _extract_entities(texts, limit=24),
        "summary_keywords": _extract_keywords(texts, limit=24),
        "summary_relations": _extract_relation_phrases(texts, limit=12),
    }


def summarize_pages(
    pages: Iterable[OCRPage],
    title: str,
    reading_id: str,
    window_size: int = 10,
    window_target_words: int = 1000,
    window_hard_cap_words: int = 2000,
    merge_target_words: int = 1000,
    merge_hard_cap_words: int = 2000,
) -> ReadingSummary:
    windows: list[PageWindowSummary] = []
    for index, group in enumerate(_group_pages(pages, window_size), start=1):
        windows.append(
            summarize_window(
                title=title,
                reading_id=reading_id,
                window_index=index,
                window=group,
                target_words=window_target_words,
                hard_cap_words=window_hard_cap_words,
            )
        )

    merged_summary = (
        merge_window_summaries(
            title=title,
            reading_id=reading_id,
            windows=windows,
            target_words=merge_target_words,
            hard_cap_words=merge_hard_cap_words,
        )
        if windows
        else None
    )
    summary_signals = _derive_summary_signals(windows, merged_summary)

    return ReadingSummary(
        reading_id=reading_id,
        title=title,
        window_size=window_size,
        window_target_words=window_target_words,
        window_hard_cap_words=window_hard_cap_words,
        merge_target_words=merge_target_words,
        merge_hard_cap_words=merge_hard_cap_words,
        llm_model=getattr(getattr(Settings, "llm", None), "model", None),
        windows=windows,
        merged_summary=merged_summary,
        summary_entities=summary_signals["summary_entities"],
        summary_keywords=summary_signals["summary_keywords"],
        summary_relations=summary_signals["summary_relations"],
    )


def summary_markdown(summary: ReadingSummary) -> str:
    lines = [
        f"# Summary: {summary.title}",
        "",
        f"- Reading ID: {summary.reading_id}",
        f"- Window size: {summary.window_size} pages",
        f"- Window target words: {summary.window_target_words}",
        f"- Window hard cap: {summary.window_hard_cap_words}",
        f"- Merge target words: {summary.merge_target_words}",
        f"- Merge hard cap: {summary.merge_hard_cap_words}",
    ]
    if summary.llm_model:
        lines.append(f"- LLM model: {summary.llm_model}")
    lines.append("")
    for window in summary.windows:
        lines.extend([
            f"## Pages {window.page_start}-{window.page_end}",
            window.text,
            "",
        ])
    if summary.merged_summary:
        lines.extend(["## Document summary", summary.merged_summary, ""])
    return "\n".join(lines).strip() + "\n"


def configure_summary_llm(ollama_base_url: str, llm_model: str | None) -> str | None:
    if not llm_model:
        return None
    try:
        from llama_index.llms.ollama import Ollama

        Settings.llm = Ollama(model=llm_model, base_url=ollama_base_url, request_timeout=600.0)
        return llm_model
    except Exception:
        return None


def summarize_reading(
    reading_id: str,
    base_dir: str | Path = "data/ocr",
    window_size: int = 10,
    window_target_words: int = 1000,
    window_hard_cap_words: int = 2000,
    merge_target_words: int = 1000,
    merge_hard_cap_words: int = 2000,
    ollama_base_url: str = "http://localhost:11434",
    llm_model: str | None = "qwen2.5-deterministic",
) -> ReadingSummary:
    reading_dir = Path(base_dir) / reading_id
    metadata = ReadingMetadata(**load_metadata(reading_dir))
    pages = [OCRPage(**page) for page in load_pages(reading_dir)]
    effective_llm_model = configure_summary_llm(ollama_base_url, llm_model)
    summary = summarize_pages(
        pages=pages,
        title=metadata.title,
        reading_id=reading_id,
        window_size=window_size,
        window_target_words=window_target_words,
        window_hard_cap_words=window_hard_cap_words,
        merge_target_words=merge_target_words,
        merge_hard_cap_words=merge_hard_cap_words,
    )
    save_summary_artifacts(reading_dir, summary)
    metadata.summary_window_size = window_size
    metadata.summary_window_target_words = window_target_words
    metadata.summary_window_hard_cap_words = window_hard_cap_words
    metadata.summary_merge_target_words = merge_target_words
    metadata.summary_merge_hard_cap_words = merge_hard_cap_words
    metadata.summary_window_max_words = window_target_words
    metadata.summary_merge_max_words = merge_target_words
    metadata.summary_model = effective_llm_model
    metadata.summary_generated_at = datetime.now(timezone.utc).isoformat()
    save_metadata(reading_dir, metadata)
    return summary


def _sanitize_mermaid_label(text: str, max_words: int = 8) -> str:
    cleaned = re.sub(r"[^\w\s'-]", "", text).strip()
    words = cleaned.split()
    if len(words) > max_words:
        words = words[:max_words]
    label = " ".join(words).strip()
    return label or "event"


def build_study_materials(summary: ReadingSummary) -> str:
    lines = [
        f"# Study Materials: {summary.title}",
        "",
        "## Quick facts",
        f"- Reading ID: {summary.reading_id}",
        f"- Window size: {summary.window_size} pages",
        f"- Windows: {len(summary.windows)}",
        "",
        "## Summary entities",
        ", ".join(summary.summary_entities[:12]) if summary.summary_entities else "(none)",
        "",
        "## Key terms",
        ", ".join(summary.summary_keywords[:12]) if summary.summary_keywords else "(none)",
        "",
        "## Mind map",
        "```mermaid",
        "mindmap",
        f"  root(({_sanitize_mermaid_label(summary.title, max_words=6)}))",
    ]
    for window in summary.windows:
        lines.append(f"    Pages {window.page_start}-{window.page_end}")
        preview = re.split(r"[\.!?]", window.text.strip(), maxsplit=1)[0].strip()
        if preview:
            lines.append(f"      {_sanitize_mermaid_label(preview, max_words=10)}")
    lines.extend([
        "```",
        "",
        "## Window timeline",
    ])
    for window in summary.windows:
        preview = re.split(r"[\.!?]", window.text.strip(), maxsplit=1)[0].strip()
        lines.append(f"- Pages {window.page_start}-{window.page_end}: {preview}")
    lines.extend([
        "",
        "## Document summary",
        summary.merged_summary or "",
        "",
        "## Study prompts",
        "- What is the central conflict?",
        "- Who drives the main action?",
        "- What changes from the beginning to the end?",
        "- Which relationships matter most?",
        "- What symbols or objects recur?",
    ])
    return "\n".join(lines).strip() + "\n"


def save_summary_artifacts(reading_dir: str | Path, summary: ReadingSummary) -> dict[str, Path]:
    reading_dir = Path(reading_dir)
    summaries_dir = reading_dir / "summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    windows_path = summaries_dir / "window_summaries.json"
    merged_path = summaries_dir / "summary.json"
    markdown_path = summaries_dir / "summary.md"
    study_path = summaries_dir / "study_materials.md"

    windows_path.write_text(
        json.dumps([window.to_dict() for window in summary.windows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    merged_path.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    markdown_path.write_text(summary_markdown(summary), encoding="utf-8")
    study_path.write_text(build_study_materials(summary), encoding="utf-8")

    return {
        "windows": windows_path,
        "summary": merged_path,
        "markdown": markdown_path,
        "study": study_path,
    }
