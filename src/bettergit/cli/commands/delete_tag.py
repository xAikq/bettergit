from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError

def register(app: typer.Typer) -> None:
    """Register the `bg delete-tag` command."""

    @app.command("delete-tag", help="Delete your tag by name.")
    def delete_tag_cmd(
        name: str,
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file.")
    ):
        resolve_config(config_path)
        try:
            gitio.delete_tag(name)
        except GitError as exc:
            show_error("delete-tag", str(exc))
            raise typer.Exit(code=1)
        show_success("delete-tag", name)