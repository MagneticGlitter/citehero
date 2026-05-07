from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from app.persist import load_metadata, load_pages
from app.pipeline import ingest_reading


def _cmd_ingest(args: argparse.Namespace) -> int:
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


def _cmd_list(args: argparse.Namespace) -> int:
    base = Path(args.base_dir)
    if not base.exists():
        return 0
    for path in sorted(base.iterdir()):
        if path.is_dir():
            print(path.name)
    return 0


def _cmd_page(args: argparse.Namespace) -> int:
    reading_dir = Path(args.base_dir) / args.reading_id
    pages = load_pages(reading_dir)
    for page in pages:
        if int(page["page_number"]) == args.page:
            print(page["text"])
            return 0
    raise SystemExit(f"page {args.page} not found")


def _cmd_meta(args: argparse.Namespace) -> int:
    reading_dir = Path(args.base_dir) / args.reading_id
    print(json.dumps(load_metadata(reading_dir), indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local reading assistant CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="OCR and index a PDF")
    ingest.add_argument("--file", required=True, type=Path)
    ingest.add_argument("--reading-id")
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--author")
    ingest.add_argument("--course")
    ingest.add_argument("--lecture")
    ingest.add_argument("--base-dir", default="data/ocr")
    ingest.add_argument("--dpi", type=int, default=200)
    ingest.add_argument("--lang", default="en")
    ingest.add_argument("--renderer", choices=("auto", "pymupdf"), default="auto")
    ingest.add_argument("--embedding-backend", choices=("auto", "ollama", "mock"), default="auto")
    ingest.add_argument("--ollama-base-url", default="http://localhost:11434")
    ingest.add_argument("--embed-model", default="nomic-embed-text")
    ingest.add_argument("--llm-model")
    ingest.set_defaults(func=_cmd_ingest)

    list_cmd = sub.add_parser("list", help="List ingested readings")
    list_cmd.add_argument("--base-dir", default="data/ocr")
    list_cmd.set_defaults(func=_cmd_list)

    page = sub.add_parser("page", help="Print one extracted page")
    page.add_argument("--base-dir", default="data/ocr")
    page.add_argument("--reading-id")
    page.add_argument("--page", type=int, required=True)
    page.set_defaults(func=_cmd_page)

    meta = sub.add_parser("meta", help="Print reading metadata")
    meta.add_argument("--base-dir", default="data/ocr")
    meta.add_argument("--reading-id")
    meta.set_defaults(func=_cmd_meta)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
