from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from PIL import Image


@dataclass(slots=True)
class RenderedPage:
    page_number: int
    image: Image.Image
    renderer: str
    width_px: int
    height_px: int
    source_path: str


def _iter_rendered_with_pymupdf(pdf_path: Path, dpi: int) -> Iterator[RenderedPage]:
    import fitz  # type: ignore[import-not-found]

    doc = fitz.open(str(pdf_path))
    try:
        zoom = dpi / 72.0
        matrix = fitz.Matrix(zoom, zoom)
        for index in range(doc.page_count):
            page_number = index + 1
            page = doc.load_page(index)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            try:
                image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                yield RenderedPage(
                    page_number=page_number,
                    image=image,
                    renderer="pymupdf",
                    width_px=pix.width,
                    height_px=pix.height,
                    source_path=str(pdf_path),
                )
            finally:
                # Help large PDFs release memory before moving to the next page.
                page = None
                pix = None
    finally:
        doc.close()


def render_pdf_pages(pdf_path: str | Path, dpi: int = 200, renderer: str = "auto") -> Iterator[RenderedPage]:
    pdf_path = Path(pdf_path)
    yield from _iter_rendered_with_pymupdf(pdf_path, dpi)


def iter_pdf_pages(pdf_path: str | Path, dpi: int = 200, renderer: str = "auto") -> Iterator[RenderedPage]:
    yield from render_pdf_pages(pdf_path, dpi=dpi, renderer=renderer)
