from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register the `bg branches` command."""

    @app.command("branches", help="Show a list of branches.")
    def branches(
        all_: bool = typer.Option(False, "--all", "-a", help="Include remote branches."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            current = gitio.current_branch()
            items = gitio.list_branches(all_=all_)
        except GitError as exc:
            show_error("branches", message=str(exc))
            raise typer.Exit(code=1)

        show_success("branches", "list")
        for name in items:
            prefix = "*" if name == current else " "
            typer.echo(f"{prefix} {name}")
