from __future__ import annotations

import sys
from pathlib import Path

# Compatibility wrapper for running from the checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from app.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
