from __future__ import annotations

from typing import Optional

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success, style_prompt
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
        remote: str = typer.Option("origin", "--remote", "-r", help="Remote name used pushing tags."),
        config_path: str | None = typer.Option(None, "--config", "-c", help="Path to a configuration file.")
    ):
        resolve_config(config_path)
        try:
            gitio.create_tag(name, message)
            prompt = style_prompt(f"Push {name} to {remote} as well?")
            should_push = typer.confirm(prompt, default=False)

            if should_push:
                try:
                    gitio.push_tag(name, remote)
                    show_success("push-tag", f"{name}/{remote}", remote)
                except GitError as exc:
                    show_error("push-tag", f"{name}/{remote}", str(exc))
                    raise typer.Exit(code=1)

        except GitError as exc:
            show_error("create-tag", str(exc))
            raise typer.Exit(code=1)
        show_success("create-tag")