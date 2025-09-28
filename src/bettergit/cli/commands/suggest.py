from __future__ import annotations

import shutil
from typing import Optional

import typer

from bettergit.cli.utils import (
    echo_boxed,
    ensure_staged_changes_or_exit,
    resolve_config,
    show_error,
    show_success,
    style_prompt,
)
from bettergit.core import classify, gitio, template
from bettergit.core.gitio import GitError
from bettergit.llm import generate_commit as llm_generate


def register(app: typer.Typer) -> None:
    """Register the `bg suggest` command."""

    @app.command("suggest", help="Generate a commit message from staged diff and ask for confirmation.")
    def suggest(
        config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
        llm_override: Optional[bool] = typer.Option(
            None,
            "--llm/--no-llm",
            help="Force enable or disable the LLM for this invocation.",
        ),
    ) -> None:
        cfg = resolve_config(config_path)
        use_llm = llm_override if llm_override is not None else cfg.llm.enabled

        diff = ensure_staged_changes_or_exit()
        files = gitio.get_changed_files()
        commit_type, scope = classify.detect_type_scope(diff, files, cfg)

        def build_message() -> str:
            added, removed = template.summarize_diff(diff)
            if use_llm:
                result = llm_generate(diff, files, commit_type, scope, added, removed, cfg)
                return template.render_commit(
                    result["type"],
                    result.get("scope"),
                    result.get("summary", ""),
                    result.get("body"),
                    cfg,
                )
            summary = template.build_summary(commit_type, scope, added, removed, cfg)
            return template.render_commit(commit_type, scope, summary, body=None, cfg=cfg)

        message = build_message()
        needs_redraw = True
        previous_width = shutil.get_terminal_size((80, 20)).columns

        while True:
            width = shutil.get_terminal_size((80, 20)).columns
            if width != previous_width:
                needs_redraw = True
                previous_width = width
            if needs_redraw:
                echo_boxed(message)
                needs_redraw = False

            prompt = style_prompt("Action? [c]ommit / [e]dit / [r]egen / [q]uit")
            choice = typer.prompt(prompt).strip().lower()

            if choice in {"e", "edit"}:
                typer.secho("Opening editor...", fg=typer.colors.BLUE)
                edited = typer.edit(message)
                if edited is None:
                    typer.secho("Edit cancelled.", fg=typer.colors.YELLOW)
                    continue
                message = edited.rstrip()
                needs_redraw = True
                continue

            if choice in {"r", "regen", "regenerate"}:
                typer.secho("Regenerating", fg=typer.colors.BLUE)
                message = build_message()
                needs_redraw = True
                continue

            if choice in {"c", "commit", "y", "yes"}:
                try:
                    gitio.commit(message)
                except GitError as exc:
                    show_error("commit", message=str(exc))
                    raise typer.Exit(code=1)
                show_success("commit", gitio.current_branch())
                return

            if choice in {"q", "quit", "n", "no", "cancel", "exit"}:
                typer.secho("Aborted.", fg=typer.colors.YELLOW)
                return

            typer.secho("Please choose: c for commit, e for edit, r for regenerate, q for quit.", fg=typer.colors.YELLOW)
