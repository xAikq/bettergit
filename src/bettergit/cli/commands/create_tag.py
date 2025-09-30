from __future__ import annotations

from typing import Optional

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError

def register(app: typer.Typer) -> None:
    """Register the `bg create-tag` command."""

    @app.command("create-tag", help="Create a new tag for your releases.")
    def create_tag_cmd(
        name: str,
        message: Optional[str] = typer.Argument(
            None,
            help="Your message.",
        ),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file.")
    ):
        resolve_config(config_path)
        try:
            gitio.create_tag(name, message)
        except GitError as exc:
            show_error("create-tag", str(exc))
            raise typer.Exit(code=1)
        show_success("create-tag")