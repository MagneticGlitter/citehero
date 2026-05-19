from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from app.investigator import investigate_reading, investigation_markdown
from app.persist import load_metadata, load_pages
from app.pipeline import ingest_reading
from app.summary import summarize_reading


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


def _cmd_summarize(args: argparse.Namespace) -> int:
    summary = summarize_reading(
        reading_id=args.reading_id,
        base_dir=args.base_dir,
        window_size=args.summary_window_size,
        window_target_words=args.summary_window_target_words,
        window_hard_cap_words=args.summary_window_hard_cap_words,
        merge_target_words=args.summary_merge_target_words,
        merge_hard_cap_words=args.summary_merge_hard_cap_words,
        ollama_base_url=args.ollama_base_url,
        llm_model=args.llm_model,
    )
    print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
    return 0


def _cmd_ask(args: argparse.Namespace) -> int:
    result = investigate_reading(
        reading_id=args.reading_id,
        question=args.question,
        base_dir=args.base_dir,
        top_k=args.top_k,
    )
    print(investigation_markdown(result))
    return 0


def _cmd_study(args: argparse.Namespace) -> int:
    reading_dir = Path(args.base_dir) / args.reading_id / "summaries" / "study_materials.md"
    if not reading_dir.exists():
        raise SystemExit("study materials not found; run `python main.py summarize --reading-id ...` first")
    print(reading_dir.read_text(encoding="utf-8"))
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

    summarize = sub.add_parser("summarize", help="Build window and document summaries")
    summarize.add_argument("--base-dir", default="data/ocr")
    summarize.add_argument("--reading-id", required=True)
    summarize.add_argument("--ollama-base-url", default="http://localhost:11434")
    summarize.add_argument("--llm-model", default="qwen2.5-deterministic")
    summarize.add_argument("--summary-window-size", type=int, default=10)
    summarize.add_argument("--summary-window-target-words", type=int, default=1000)
    summarize.add_argument("--summary-window-hard-cap-words", type=int, default=2000)
    summarize.add_argument("--summary-merge-target-words", type=int, default=1000)
    summarize.add_argument("--summary-merge-hard-cap-words", type=int, default=2000)
    summarize.set_defaults(func=_cmd_summarize)

    ask = sub.add_parser("ask", help="Answer a question with grounded retrieval")
    ask.add_argument("--base-dir", default="data/ocr")
    ask.add_argument("--reading-id", required=True)
    ask.add_argument("--question", required=True)
    ask.add_argument("--top-k", type=int, default=10)
    ask.set_defaults(func=_cmd_ask)

    study = sub.add_parser("study", help="Print study materials built from summary.json")
    study.add_argument("--base-dir", default="data/ocr")
    study.add_argument("--reading-id", required=True)
    study.set_defaults(func=_cmd_study)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
