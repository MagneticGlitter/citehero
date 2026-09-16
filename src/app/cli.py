from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import resolve_base_dir, resolve_prompt_formats_dir, resolved_paths
from .investigator import investigate_reading, investigation_markdown
from .persist import load_metadata, load_pages
from .pipeline import ingest_reading
from .summary import summarize_reading


def _cmd_ingest(args: argparse.Namespace) -> int:
    reading_dir = ingest_reading(
        args.file,
        reading_id=args.reading_id,
        title=args.title,
        author=args.author,
        course=args.course,
        lecture=args.lecture,
        base_dir=resolve_base_dir(args.base_dir),
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
    base = resolve_base_dir(args.base_dir)
    if not base.exists():
        return 0
    for path in sorted(base.iterdir()):
        if path.is_dir():
            print(path.name)
    return 0


def _cmd_page(args: argparse.Namespace) -> int:
    reading_dir = resolve_base_dir(args.base_dir) / args.reading_id
    pages = load_pages(reading_dir)
    for page in pages:
        if int(page["page_number"]) == args.page:
            print(page["text"])
            return 0
    raise SystemExit(f"page {args.page} not found")


def _cmd_meta(args: argparse.Namespace) -> int:
    reading_dir = resolve_base_dir(args.base_dir) / args.reading_id
    print(json.dumps(load_metadata(reading_dir), indent=2, ensure_ascii=False))
    return 0


def _cmd_summarize(args: argparse.Namespace) -> int:
    summary = summarize_reading(
        reading_id=args.reading_id,
        base_dir=resolve_base_dir(args.base_dir),
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
        base_dir=resolve_base_dir(args.base_dir),
        top_k=args.top_k,
    )
    print(investigation_markdown(result))
    return 0


def _cmd_study(args: argparse.Namespace) -> int:
    reading_dir = resolve_base_dir(args.base_dir) / args.reading_id / "summaries" / "study_materials.md"
    if not reading_dir.exists():
        raise SystemExit("study materials not found; run `citehero summarize --reading-id ...` first")
    print(reading_dir.read_text(encoding="utf-8"))
    return 0


def _cmd_paths(args: argparse.Namespace) -> int:
    paths = resolved_paths(args.base_dir, args.prompt_formats_dir, args.config)
    if args.json:
        print(json.dumps(paths, indent=2, ensure_ascii=False))
    else:
        for key, value in paths.items():
            print(f"{key}: {value}")
    return 0


def _safe_prompt_path(root: Path, relative: str | None = None) -> Path:
    target = root if not relative else root / relative
    resolved = target.resolve()
    if root.resolve() not in (resolved, *resolved.parents):
        raise SystemExit(f"prompt path escapes prompt format root: {relative}")
    return resolved


def _cmd_prompt_dir(args: argparse.Namespace) -> int:
    print(resolve_prompt_formats_dir(args.prompt_formats_dir))
    return 0


def _cmd_prompt_list(args: argparse.Namespace) -> int:
    root = resolve_prompt_formats_dir(args.prompt_formats_dir)
    if not root.exists():
        raise SystemExit(f"prompt formats directory not found: {root}")
    pattern = args.glob or "**/*.md"
    for path in sorted(root.glob(pattern)):
        if path.is_file():
            print(path.relative_to(root))
    return 0


def _cmd_prompt_read(args: argparse.Namespace) -> int:
    root = resolve_prompt_formats_dir(args.prompt_formats_dir)
    path = _safe_prompt_path(root, args.path)
    if not path.exists() or not path.is_file():
        raise SystemExit(f"prompt format not found: {path}")
    print(path.read_text(encoding="utf-8"))
    return 0


def _add_base_dir(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--base-dir",
        default=None,
        help="OCR data directory. Defaults to CITEHERO_BASE_DIR, config, or the checkout's data/ocr.",
    )


def _add_prompt_formats_dir(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--prompt-formats-dir",
        default=None,
        help="Prompt formats directory. Defaults to CITEHERO_PROMPT_FORMATS_DIR, config, or the checkout's prompt-formats.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Local reading assistant CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="OCR and index a PDF")
    ingest.add_argument("--file", required=True, type=Path)
    ingest.add_argument("--reading-id")
    ingest.add_argument("--title", required=True)
    ingest.add_argument("--author")
    ingest.add_argument("--course")
    ingest.add_argument("--lecture")
    _add_base_dir(ingest)
    ingest.add_argument("--dpi", type=int, default=120)
    ingest.add_argument("--lang", default="en")
    ingest.add_argument("--renderer", choices=("auto", "pymupdf"), default="auto")
    ingest.add_argument("--embedding-backend", choices=("auto", "ollama", "mock"), default="auto")
    ingest.add_argument("--ollama-base-url", default="http://localhost:11434")
    ingest.add_argument("--embed-model", default="nomic-embed-text")
    ingest.set_defaults(func=_cmd_ingest)

    list_cmd = sub.add_parser("list", help="List ingested readings")
    _add_base_dir(list_cmd)
    list_cmd.set_defaults(func=_cmd_list)

    page = sub.add_parser("page", help="Print one extracted page")
    _add_base_dir(page)
    page.add_argument("--reading-id", required=True)
    page.add_argument("--page", type=int, required=True)
    page.set_defaults(func=_cmd_page)

    meta = sub.add_parser("meta", help="Print reading metadata")
    _add_base_dir(meta)
    meta.add_argument("--reading-id", required=True)
    meta.set_defaults(func=_cmd_meta)

    summarize = sub.add_parser("summarize", help="Build window and document summaries")
    _add_base_dir(summarize)
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
    _add_base_dir(ask)
    ask.add_argument("--reading-id", required=True)
    ask.add_argument("--question", required=True)
    ask.add_argument("--top-k", type=int, default=10)
    ask.set_defaults(func=_cmd_ask)

    study = sub.add_parser("study", help="Print study materials built from summary.json")
    _add_base_dir(study)
    study.add_argument("--reading-id", required=True)
    study.set_defaults(func=_cmd_study)

    paths = sub.add_parser("paths", help="Print resolved citehero paths")
    _add_base_dir(paths)
    _add_prompt_formats_dir(paths)
    paths.add_argument("--config", default=None, help="Config JSON path")
    paths.add_argument("--json", action="store_true", help="Print JSON")
    paths.set_defaults(func=_cmd_paths)

    prompt = sub.add_parser("prompt", help="Inspect injectable prompt formats")
    prompt_sub = prompt.add_subparsers(dest="prompt_command", required=True)

    prompt_dir = prompt_sub.add_parser("dir", help="Print resolved prompt formats directory")
    _add_prompt_formats_dir(prompt_dir)
    prompt_dir.set_defaults(func=_cmd_prompt_dir)

    prompt_list = prompt_sub.add_parser("list", help="List prompt format markdown files")
    _add_prompt_formats_dir(prompt_list)
    prompt_list.add_argument("--glob", default="**/*.md", help="Glob relative to prompt formats root")
    prompt_list.set_defaults(func=_cmd_prompt_list)

    prompt_read = prompt_sub.add_parser("read", help="Read one prompt format file")
    _add_prompt_formats_dir(prompt_read)
    prompt_read.add_argument("path", help="Path relative to prompt formats root, e.g. essay-writing/README.md")
    prompt_read.set_defaults(func=_cmd_prompt_read)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
