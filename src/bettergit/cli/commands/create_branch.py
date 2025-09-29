from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import branchmeta
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register the `bg create-branch` command."""

    @app.command("create-branch", help="Create a new branch, optionally switching to it.")
    def create_branch_cmd(
        branch: str = typer.Argument(..., help="Name of the new branch."),
        start_point: str | None = typer.Option(
            None,
            "--from",
            "-f",
            help="Create the branch starting from this commit/branch (defaults to HEAD).",
        ),
        no_switch: bool = typer.Option(False, "--no-switch", help="Create the branch but stay on the current one."),
        force: bool = typer.Option(False, "--force", "-F", help="Overwrite an existing branch."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            gitio.create_branch(
                branch_name=branch,
                start_point=start_point,
                checkout=not no_switch,
                force=force,
            )
            branchmeta.record_origin(branch, start_point)
        except GitError as exc:
            show_error("create-branch", branch, str(exc))
            raise typer.Exit(code=1)

        notes: list[str] = []
        if start_point:
            notes.append(f"from {start_point}")
        if force:
            notes.append("force")
        if no_switch:
            notes.append("no switch")
        note = ", ".join(notes) if notes else None
        show_success("create-branch", branch, note)
