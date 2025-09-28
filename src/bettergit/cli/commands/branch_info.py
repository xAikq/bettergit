from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register the `bg branch-info` command."""

    @app.command("branch-info", help="Show concise information about a branch.")
    def branch_info(
        branch: str | None = typer.Option(None, "--branch", "-b", help="Branch name (defaults to current)."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            info = gitio.branch_info(branch)
        except GitError as exc:
            name = branch or "(current)"
            show_error("branch-info", name, str(exc))
            raise typer.Exit(code=1)

        show_success("branch-info", info.name)

        def render(label: str, value: str | None) -> None:
            typer.echo(f"{label.rjust(10)} | {value or '-'}")

        render("tracking", info.tracking)
        render("ahead", str(info.ahead))
        render("behind", str(info.behind))
        if info.last_commit_sha:
            typer.echo(" last-commit")
            render("sha", info.last_commit_sha[:12])
            render("title", info.last_commit_title)
            render("author", info.last_commit_author)
            render("date", info.last_commit_date)
