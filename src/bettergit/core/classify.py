from __future__ import annotations

from pathlib import Path
from typing import Iterable

__all__ = ["detect_type_scope"]

_KEYWORDS_FIX = ("fix", "bug", "error", "exception")


def detect_type_scope(diff: str, files: Iterable[str], cfg) -> tuple[str, str | None]:
    """Return a tuple of (type, scope) inferred from *diff* and *files*."""

    staged_files = list(files)
    scope = _infer_scope(staged_files)
    change_type = _infer_type(diff, staged_files)
    return change_type, scope


def _infer_scope(files: list[str]) -> str | None:
    if not files:
        return None
    parts = Path(files[0]).parts
    return parts[0] if parts else None


def _infer_type(diff: str, files: list[str]) -> str:
    if files and all(path.startswith("tests/") for path in files):
        return "test"
    if files and any(path.lower().startswith("docs/") or path.lower().endswith("readme.md") for path in files):
        return "docs"

    lowered = diff.lower()
    if any(keyword in lowered for keyword in _KEYWORDS_FIX):
        return "fix"
    return "feat"
