from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class OCRLine:
    text: str
    confidence: float | None = None
    bbox: list[list[float]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OCRPage:
    reading_id: str
    title: str
    author: str | None
    page_number: int
    text: str
    ocr_engine: str
    confidence: float | None = None
    source_path: str | None = None
    renderer: str | None = None
    lines: list[OCRLine] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["lines"] = [line.to_dict() for line in self.lines]
        return payload


@dataclass(slots=True)
class ReadingMetadata:
    reading_id: str
    title: str
    author: str | None = None
    course: str | None = None
    lecture: str | None = None
    source_path: str | None = None
    created_at: str | None = None
    dpi: int | None = None
    ocr_engine: str | None = None
    renderer: str | None = None
    embedding_backend: str | None = None
    embed_model: str | None = None
    llm_model: str | None = None
    summary_window_size: int | None = None
    summary_window_target_words: int | None = None
    summary_window_hard_cap_words: int | None = None
    summary_merge_target_words: int | None = None
    summary_merge_hard_cap_words: int | None = None
    summary_window_max_words: int | None = None
    summary_merge_max_words: int | None = None
    summary_model: str | None = None
    summary_generated_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReadingBundle:
    metadata: ReadingMetadata
    pages: list[OCRPage] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": self.metadata.to_dict(),
            "pages": [page.to_dict() for page in self.pages],
        }


def default_reading_dir(base_dir: str | Path, reading_id: str) -> Path:
    return Path(base_dir) / reading_id
