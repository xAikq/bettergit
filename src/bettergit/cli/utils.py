from __future__ import annotations

import shutil
import textwrap
from typing import Optional

import typer

from bettergit import config as config_pkg
from bettergit.config import Config
from bettergit.core import gitio

__all__ = [
    "format_success",
    "format_error",
    "show_success",
    "show_error",
    "ensure_staged_changes_or_exit",
    "echo_boxed",
    "style_prompt",
    "resolve_config",
]

_ARROW = "->"


def format_success(action: str, target: Optional[str] = None, note: Optional[str] = None) -> str:
    parts = [f"[OK] {action}"]
    if target:
        parts.append(f"{_ARROW} {target}")
    if note:
        parts.append(f"({note})")
    return " ".join(parts)


def format_error(action: str, target: Optional[str] = None) -> str:
    parts = [f"[ERR] {action}"]
    if target:
        parts.append(f"{_ARROW} {target}")
    return " ".join(parts)


def show_success(action: str, target: Optional[str] = None, note: Optional[str] = None) -> None:
    typer.secho(format_success(action, target, note), fg=typer.colors.GREEN)


def show_error(action: str, target: Optional[str] = None, message: Optional[str] = None) -> None:
    typer.secho(format_error(action, target), fg=typer.colors.RED, err=True)
    if message:
        typer.secho(message, fg=typer.colors.RED, err=True)


def ensure_staged_changes_or_exit() -> str:
    diff = gitio.get_staged_diff()
    if not diff.strip():
        typer.secho(
            "[ERR] no staged changes. Run `git add ...` and try again.",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)
    return diff


def _ascii_box_lines(message: str, padding: int, max_width: int) -> tuple[str, list[str], str]:
    wrapped = textwrap.wrap(message, width=max_width) or [""]
    inner_width = max(len(line) for line in wrapped)
    top = "+" + "-" * (inner_width + padding * 2) + "+"
    bottom = top
    return top, wrapped, bottom, inner_width


def echo_boxed(
    message: str,
    *,
    padding: int = 1,
    max_width: Optional[int] = None,
    hard_limit: int = 110,
) -> None:
    columns = shutil.get_terminal_size((80, 20)).columns
    width = max_width or (columns - 4)
    width = max(10, min(hard_limit, width))

    top, lines, bottom, inner_width = _ascii_box_lines(message, padding, width)
    typer.secho(top, fg=typer.colors.BRIGHT_CYAN)
    for line in lines:
        content = line.ljust(inner_width)
        typer.secho(
            f"|{' ' * padding}{content}{' ' * padding}|",
            fg=typer.colors.BRIGHT_CYAN,
        )
    typer.secho(bottom, fg=typer.colors.BRIGHT_CYAN)


def style_prompt(text: str) -> str:
    return typer.style(text, fg=typer.colors.BRIGHT_YELLOW)


def resolve_config(path: Optional[str]) -> Config:
    return config_pkg.load_config(path)
