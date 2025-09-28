from __future__ import annotations

from typing import Optional

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register the `bg add` command."""

    @app.command("add", help="Stage files for the next commit.")
    def add_cmd(
        paths: Optional[list[str]] = typer.Argument(
            None,
            metavar="[PATH...]",
            help="Specific files or directories to stage (defaults to all).",
        ),
        config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            if not paths:
                gitio.add_all()
                show_success("add", "all")
            else:
                gitio.add(list(paths))
                show_success("add", ", ".join(paths))
        except GitError as exc:
            target = ", ".join(paths or ("all",))
            show_error("add", target, str(exc))
            raise typer.Exit(code=1)
