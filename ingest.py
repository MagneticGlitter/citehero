from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from app.pipeline import ingest_reading


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OCR a chapter PDF page-by-page and build a local LlamaIndex index.")
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--reading-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--author")
    parser.add_argument("--course")
    parser.add_argument("--lecture")
    parser.add_argument("--base-dir", default="data/ocr")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--lang", default="en")
    parser.add_argument("--renderer", choices=("auto", "pymupdf"), default="auto")
    parser.add_argument("--embedding-backend", choices=("auto", "ollama", "mock"), default="auto")
    parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    parser.add_argument("--embed-model", default="nomic-embed-text")
    parser.add_argument("--llm-model")
    args = parser.parse_args(argv)

    reading_dir = ingest_reading(
        args.file,
        reading_id=args.reading_id,
        title=args.title,
        author=args.author,
        course=args.course,
        lecture=args.lecture,
        base_dir=args.base_dir,
        dpi=args.dpi,
        lang=args.lang,
        renderer=args.renderer,
        embedding_backend=args.embedding_backend,
        ollama_base_url=args.ollama_base_url,
        embed_model=args.embed_model,
        llm_model=args.llm_model,
    )
    print(reading_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
