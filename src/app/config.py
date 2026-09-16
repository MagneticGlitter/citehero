from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

ENV_BASE_DIR = "CITEHERO_BASE_DIR"
ENV_PROMPT_FORMATS_DIR = "CITEHERO_PROMPT_FORMATS_DIR"
ENV_CONFIG = "CITEHERO_CONFIG"


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_config_path() -> Path:
    return Path(os.environ.get(ENV_CONFIG, "~/.config/citehero/config.json")).expanduser()


def load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(config_path).expanduser() if config_path else default_config_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _resolve_path(value: str | Path) -> Path:
    return Path(value).expanduser().resolve()


def resolve_base_dir(base_dir: str | Path | None = None, config: dict[str, Any] | None = None) -> Path:
    """Resolve OCR/index storage.

    Precedence:
    1. explicit CLI/tool argument
    2. CITEHERO_BASE_DIR
    3. ~/.config/citehero/config.json: base_dir
    4. this checkout's data/ocr if present
    5. ./data/ocr relative to current working directory
    """
    if base_dir:
        return _resolve_path(base_dir)
    if os.environ.get(ENV_BASE_DIR):
        return _resolve_path(os.environ[ENV_BASE_DIR])
    config = config if config is not None else load_config()
    if config.get("base_dir"):
        return _resolve_path(config["base_dir"])
    repo_default = project_root() / "data" / "ocr"
    if repo_default.exists():
        return repo_default.resolve()
    return (Path.cwd() / "data" / "ocr").resolve()


def resolve_prompt_formats_dir(prompt_formats_dir: str | Path | None = None, config: dict[str, Any] | None = None) -> Path:
    """Resolve prompt-format library directory.

    Precedence:
    1. explicit CLI/tool argument
    2. CITEHERO_PROMPT_FORMATS_DIR
    3. ~/.config/citehero/config.json: prompt_formats_dir
    4. this checkout's prompt-formats if present
    5. ./prompt-formats relative to current working directory
    """
    if prompt_formats_dir:
        return _resolve_path(prompt_formats_dir)
    if os.environ.get(ENV_PROMPT_FORMATS_DIR):
        return _resolve_path(os.environ[ENV_PROMPT_FORMATS_DIR])
    config = config if config is not None else load_config()
    if config.get("prompt_formats_dir"):
        return _resolve_path(config["prompt_formats_dir"])
    repo_default = project_root() / "prompt-formats"
    if repo_default.exists():
        return repo_default.resolve()
    return (Path.cwd() / "prompt-formats").resolve()


def resolved_paths(
    base_dir: str | Path | None = None,
    prompt_formats_dir: str | Path | None = None,
    config_path: str | Path | None = None,
) -> dict[str, str]:
    config = load_config(config_path)
    return {
        "project_root": str(project_root()),
        "config_path": str(Path(config_path).expanduser() if config_path else default_config_path()),
        "base_dir": str(resolve_base_dir(base_dir, config)),
        "prompt_formats_dir": str(resolve_prompt_formats_dir(prompt_formats_dir, config)),
    }
