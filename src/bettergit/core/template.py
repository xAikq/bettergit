from __future__ import annotations

from typing import Optional, Tuple

__all__ = [
    "generate_title",
    "summarize_diff",
    "build_summary",
    "render_commit",
]


def generate_title(diff: str, lang: str = "en") -> Optional[str]:
    """Placeholder for future summary generation in different languages."""

    return None


def summarize_diff(diff: str) -> Tuple[int, int]:
    """Return counts of added and removed lines from a unified diff."""

    added = sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff.splitlines() if line.startswith("-") and not line.startswith("---"))
    return added, removed


def build_summary(commit_type: str, scope: str | None, added: int, removed: int, cfg) -> str:
    """Build a simple textual summary used in commit headers."""

    stats = f"+{added}/-{removed}"
    return f"auto summary [{stats}]"


def render_commit(commit_type: str, scope: str | None, summary: str, body: Optional[str], cfg) -> str:
    """Render the final commit message according to Conventional Commit rules."""

    header = f"{commit_type}{f'({scope})' if scope else ''}: {summary}".strip()
    if body:
        body_block = body.strip()
        return f"{header}\n\n{body_block}\n"
    return f"{header}\n"
