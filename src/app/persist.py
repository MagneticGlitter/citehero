from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable

from .models import OCRPage, ReadingBundle, ReadingMetadata, default_reading_dir


def default_reading_id_from_path(pdf_path: str | Path) -> str:
    return Path(pdf_path).stem


def resolve_source_pdf(file_path: str | Path, raw_dir: str | Path = "data/raw") -> Path:
    path = Path(file_path).expanduser()
    if path.exists():
        return path.resolve()

    raw_dir = Path(raw_dir).expanduser()
    direct = raw_dir / path
    if direct.exists():
        return direct.resolve()

    by_name = raw_dir / path.name
    if by_name.exists():
        return by_name.resolve()

    if raw_dir.exists():
        matches = sorted(raw_dir.rglob(path.name))
        if matches:
            return matches[0].resolve()

    raise FileNotFoundError(f"could not find PDF '{file_path}' (looked in current directory and {raw_dir})")


def ensure_reading_dir(base_dir: str | Path, reading_id: str) -> Path:
    reading_dir = default_reading_dir(base_dir, reading_id)
    reading_dir.mkdir(parents=True, exist_ok=True)
    (reading_dir / "index").mkdir(parents=True, exist_ok=True)
    return reading_dir


def save_metadata(reading_dir: str | Path, metadata: ReadingMetadata) -> Path:
    path = Path(reading_dir) / "metadata.json"
    path.write_text(json.dumps(metadata.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def save_pages(reading_dir: str | Path, pages: Iterable[OCRPage]) -> Path:
    path = Path(reading_dir) / "pages.json"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("[\n")
        first = True
        for page in pages:
            if not first:
                handle.write(",\n")
            json.dump(page.to_dict(), handle, ensure_ascii=False)
            first = False
        handle.write("\n]\n")
    return path


def save_bundle(reading_dir: str | Path, bundle: ReadingBundle) -> tuple[Path, Path]:
    metadata_path = save_metadata(reading_dir, bundle.metadata)
    pages_path = save_pages(reading_dir, bundle.pages)
    return metadata_path, pages_path


def copy_source_pdf(source_pdf: str | Path, reading_dir: str | Path) -> Path:
    source_pdf = Path(source_pdf)
    target = Path(reading_dir) / "source.pdf"
    shutil.copy2(source_pdf, target)
    return target


def load_pages(reading_dir: str | Path) -> list[dict]:
    path = Path(reading_dir) / "pages.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_metadata(reading_dir: str | Path) -> dict:
    path = Path(reading_dir) / "metadata.json"
    return json.loads(path.read_text(encoding="utf-8"))
