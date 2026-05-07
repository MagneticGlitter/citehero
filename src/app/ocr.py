from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np
from PIL import Image

from .models import OCRLine, OCRPage
from .render import render_pdf_pages


@dataclass(slots=True)
class PaddleOCREngine:
    ocr: Any | None


def create_ocr(lang: str = "en") -> PaddleOCREngine:
    try:
        import os

        os.environ.setdefault("FLAGS_use_mkldnn", "0")
        os.environ.setdefault("FLAGS_use_onednn", "0")
        from paddleocr import PaddleOCR  # type: ignore[import-not-found]
    except Exception:
        return PaddleOCREngine(ocr=None)

    return PaddleOCREngine(
        ocr=PaddleOCR(
            lang=lang,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
        )
    )


def extract_pages_from_pdf(pdf_path: str | Path, dpi: int = 200, renderer: str = "auto") -> list[Any]:
    return list(render_pdf_pages(pdf_path, dpi=dpi, renderer=renderer))


def _normalize_items(raw: Any) -> list[Any]:
    if not raw:
        return []
    if isinstance(raw, tuple):
        raw = list(raw)
    if not isinstance(raw, list):
        return []
    if len(raw) == 1 and isinstance(raw[0], list):
        return raw[0]
    return raw


def _page_confidence(lines: list[OCRLine]) -> float | None:
    confidences = [line.confidence for line in lines if line.confidence is not None]
    if not confidences:
        return None
    return float(sum(confidences) / len(confidences))


def _normalize_box(box: Any) -> list[list[float]]:
    arr = np.asarray(box)
    if arr.ndim == 1:
        if arr.size % 2:
            return []
        arr = arr.reshape(-1, 2)
    return [[float(point[0]), float(point[1])] for point in arr]


def ocr_image(engine: PaddleOCREngine, image) -> tuple[str, list[OCRLine], float | None]:
    if engine.ocr is None:
        raise RuntimeError("PaddleOCR is not available; install the optional `app[ocr]` extra to OCR scanned pages.")

    array = np.asarray(image.convert("RGB"))
    raw = engine.ocr.ocr(array)
    items = _normalize_items(raw)

    parsed: list[OCRLine] = []
    if items and isinstance(items[0], dict):
        item = items[0]
        texts = item.get("rec_texts") or []
        scores = item.get("rec_scores") or []
        boxes = item.get("rec_boxes")
        if boxes is None:
            boxes = item.get("rec_polys")
        if boxes is None:
            boxes = []
        for text, confidence, box in zip(texts, scores, boxes):
            parsed.append(
                OCRLine(
                    text=str(text),
                    confidence=float(confidence) if confidence is not None else None,
                    bbox=_normalize_box(box),
                )
            )
    else:
        for item in items:
            if not item or len(item) < 2:
                continue
            box = item[0]
            record = item[1]
            if isinstance(record, (list, tuple)) and len(record) >= 2:
                text, confidence = record[0], record[1]
            else:
                text, confidence = record, None
            parsed.append(
                OCRLine(
                    text=str(text),
                    confidence=float(confidence) if confidence is not None else None,
                    bbox=_normalize_box(box),
                )
            )

    parsed.sort(key=lambda line: (min((pt[1] for pt in line.bbox), default=0.0), min((pt[0] for pt in line.bbox), default=0.0)))
    text = "\n".join(line.text for line in parsed if line.text).strip()
    return text, parsed, _page_confidence(parsed)


def ocr_pdf_by_page(
    pdf_path: str | Path,
    reading_id: str,
    title: str,
    author: str | None = None,
    dpi: int = 200,
    lang: str = "en",
    renderer: str = "auto",
) -> Iterator[OCRPage]:
    pdf_path = Path(pdf_path)

    import fitz  # type: ignore[import-not-found]

    engine: PaddleOCREngine | None = None
    doc = fitz.open(str(pdf_path))
    try:
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        for index in range(doc.page_count):
            page_number = index + 1
            page = doc.load_page(index)
            text_layer = page.get_text("text").strip()
            if text_layer:
                yield OCRPage(
                    reading_id=reading_id,
                    title=title,
                    author=author,
                    page_number=page_number,
                    text=text_layer,
                    ocr_engine="pymupdf-text",
                    confidence=None,
                    source_path=str(pdf_path),
                    renderer="pymupdf",
                    lines=[],
                )
                continue

            if engine is None:
                engine = create_ocr(lang=lang)
                if engine.ocr is None:
                    raise RuntimeError("PaddleOCR is not available; install the optional `app[ocr]` extra to OCR scanned pages.")

            pix = page.get_pixmap(matrix=matrix, alpha=False)
            try:
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                try:
                    text, lines, confidence = ocr_image(engine, image)
                    yield OCRPage(
                        reading_id=reading_id,
                        title=title,
                        author=author,
                        page_number=page_number,
                        text=text,
                        ocr_engine="paddleocr",
                        confidence=confidence,
                        source_path=str(pdf_path),
                        renderer="pymupdf",
                        lines=lines,
                    )
                finally:
                    image.close()
            finally:
                page = None
                pix = None
    finally:
        doc.close()
