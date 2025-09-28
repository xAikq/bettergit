from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success, style_prompt
from bettergit.core import gitio
from bettergit.core.gitio import GitError


def register(app: typer.Typer) -> None:
    """Register the `bg delete-branch` command."""

    @app.command(
        "delete-branch",
        help="Delete a branch locally and optionally remove it from a remote.",
    )
    def delete_branch_cmd(
        branch: str = typer.Argument(..., help="Name of the branch to delete."),
        force: bool = typer.Option(False, "--force", "-F", help="Force deletion even if not merged."),
        remote: str = typer.Option("origin", "--remote", "-r", help="Remote name used for deletion."),
        no_prompt: bool = typer.Option(False, "--no-prompt", help="Skip the remote deletion prompt."),
        remote_delete: bool = typer.Option(False, "--remote-delete", help="Delete the remote branch without prompting."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
    ) -> None:
        resolve_config(config_path)
        try:
            gitio.delete_branch(branch_name=branch, force=force)
        except GitError as exc:
            show_error("delete-branch", branch, str(exc))
            raise typer.Exit(code=1)

        note_parts = ["local"]
        if force:
            note_parts.append("force")
        show_success("delete-branch", branch, ", ".join(note_parts))

        should_delete_remote = remote_delete
        if not remote_delete and not no_prompt:
            prompt = style_prompt(f"Delete remote branch {remote}/{branch} as well?")
            should_delete_remote = typer.confirm(prompt, default=False)

        if should_delete_remote:
            try:
                gitio.delete_remote_branch(remote=remote, branch=branch)
            except GitError as exc:
                show_error("delete-branch", f"{remote}/{branch}", str(exc))
                raise typer.Exit(code=1)
            show_success("delete-branch", f"{remote}/{branch}", "remote")
        elif not no_prompt:
            typer.secho("Remote branch kept.", fg=typer.colors.YELLOW)
