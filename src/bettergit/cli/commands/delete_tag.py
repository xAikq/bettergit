from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success, style_prompt
from bettergit.core import gitio
from bettergit.core.gitio import GitError

def register(app: typer.Typer) -> None:
    """Register the `bg delete-tag` and `bg delete-remote-tag`command."""

    @app.command("delete-tag", help="Delete your tag by name (local deletion with remote deletion request).")
    def delete_tag_cmd(
        name: str,
        remote: str = typer.Option("origin", "--remote", "-r", help="Remote name used pushing tags."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file.")
    ):
        resolve_config(config_path)
        try:
            gitio.delete_tag(name)
            target = gitio.find_tag(name, remote)

            if target is not None:
                try:
                    prompt = style_prompt(f"Delete {name} from {remote} as well?")
                    should_delete = typer.confirm(prompt, default=False)
                    if should_delete:
                        try:
                            gitio.delete_remote_tag(name, remote)
                            show_success("delete-remote-tag", name)
                        except GitError as exc:
                            show_error("delete-remote-tag", str(exc))
                            raise typer.Exit(code=1)
                except GitError as exc:
                            show_error("delete-tag", str(exc))
                            raise typer.Exit(code=1)
        except GitError as exc:
            show_error("delete-tag", str(exc))
            raise typer.Exit(code=1)
        show_success("delete-tag", name)

    @app.command("delete-remote-tag", help="Deletes the tag with remote by name.")
    def delete_remote_tag_cmd(
         name: str,
         remote: str = typer.Option("origin", "--remote", "-r", help="Remote name used pushing tags."),
         config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file.")
    ):
        resolve_config(config_path)
        target = gitio.find_tag(name, remote)

        if target is not None:
            try:
                gitio.delete_remote_tag(name, remote)
            except GitError as exc:
                show_error("delete-remote-tag", str(exc))
                raise typer.Exit(code=1)
            show_success("delete-remote-tag", name)