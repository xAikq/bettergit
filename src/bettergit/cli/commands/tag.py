from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError

def register(app: typer.Typer) -> None:
    """Register the `bg tag` command."""

    @app.command("tag", help="Shows all tags.")
    def tag_cmd(
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file.")
    ):
        resolve_config(config_path)
        try:
            tags = gitio.tag()
            if tags:
                typer.echo(tags)
        except GitError as exc:
            show_error("tag", str(exc))
            raise typer.Exit(code=1)
        show_success("tag")