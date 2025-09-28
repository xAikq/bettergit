from __future__ import annotations

from typing import Optional

import typer

from bettergit.cli.utils import (
    ensure_staged_changes_or_exit,
    resolve_config,
    show_error,
    show_success,
)
from bettergit.core import classify, gitio, template
from bettergit.core.gitio import GitError
from bettergit.llm import generate_commit as llm_generate


def register(app: typer.Typer) -> None:
    """Register the `bg commit` command."""

    @app.command(
        "commit",
        help="Create a git commit with an auto-generated message (no confirmation).",
    )
    def commit(
        message_arg: Optional[str] = typer.Argument(
            None,
            metavar="[MESSAGE]",
            help="Commit message to use instead of auto-generation.",
        ),
        config_path: Optional[str] = typer.Option(None, "--config", "-c", help="Path to a configuration file."),
        llm_override: Optional[bool] = typer.Option(
            None,
            "--llm/--no-llm",
            help="Force enable or disable the LLM for this invocation.",
        ),
        message: Optional[str] = typer.Option(
            None,
            "--message",
            "-m",
            help="Commit message to use instead of auto-generation (takes precedence over heuristics).",
        ),
    ) -> None:
        cfg = resolve_config(config_path)
        use_llm = llm_override if llm_override is not None else cfg.llm.enabled

        diff = ensure_staged_changes_or_exit()

        manual_message = message if message is not None else message_arg

        if manual_message is not None:
            final_message = manual_message if manual_message.endswith("\n") else f"{manual_message}\n"
        else:
            files = gitio.get_changed_files()
            commit_type, scope = classify.detect_type_scope(diff, files, cfg)
            added, removed = template.summarize_diff(diff)

            if use_llm:
                result = llm_generate(diff, files, commit_type, scope, added, removed, cfg)
                final_message = template.render_commit(
                    result["type"],
                    result.get("scope"),
                    result.get("summary", ""),
                    result.get("body"),
                    cfg,
                )
            else:
                summary = template.build_summary(commit_type, scope, added, removed, cfg)
                final_message = template.render_commit(commit_type, scope, summary, body=None, cfg=cfg)

        try:
            gitio.commit(final_message)
        except GitError as exc:
            show_error("commit", message=str(exc))
            raise typer.Exit(code=1)
        current = gitio.current_branch()
        show_success("commit", current)
