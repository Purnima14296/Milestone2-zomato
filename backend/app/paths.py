from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    """backend/app/paths.py → parents[2] == repository root."""
    return Path(__file__).resolve().parent.parent.parent
