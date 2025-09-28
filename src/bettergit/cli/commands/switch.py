from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register the `bg switch` command."""

    @app.command("switch", help="Switch to a given branch.")
    def switch(
        branch: str = typer.Argument(..., help="Branch name."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            gitio.checkout(branch)
        except GitError as exc:
            show_error("switch", branch, str(exc))
            raise typer.Exit(code=1)
        show_success("switch", branch)
