from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register `bg push` and `bg push-to`."""

    @app.command("push", help="Push the current (or specified) branch. Sets upstream if needed.")
    def push_cmd(
        branch: str | None = typer.Option(None, "--branch", "-b", help="Branch name (defaults to current)."),
        remote: str = typer.Option("origin", "--remote", "-r", help="Remote name."),
        no_set_upstream: bool = typer.Option(False, "--no-set-upstream", help="Do not set upstream automatically."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            upstream_set = gitio.push(remote=remote, branch=branch, set_upstream=not no_set_upstream)
        except GitError as exc:
            target = branch or gitio.current_branch()
            show_error("push", f"{remote}/{target}", str(exc))
            raise typer.Exit(code=1)

        name = branch or gitio.current_branch()
        note = "upstream set" if upstream_set else None
        show_success("push", f"{remote}/{name}", note)

    @app.command("push-to", help="Push the specified branch to a remote without switching.")
    def push_to_cmd(
        branch: str = typer.Argument(..., help="Branch name to push."),
        remote: str = typer.Option("origin", "--remote", "-r", help="Remote name."),
        no_set_upstream: bool = typer.Option(False, "--no-set-upstream", help="Do not set upstream automatically."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            upstream_set = gitio.push(remote=remote, branch=branch, set_upstream=not no_set_upstream)
        except GitError as exc:
            show_error("push", f"{remote}/{branch}", str(exc))
            raise typer.Exit(code=1)

        note = "upstream set" if upstream_set else None
        show_success("push", f"{remote}/{branch}", note)
