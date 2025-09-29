from __future__ import annotations

import typer

from bettergit.cli.utils import resolve_config, show_error, show_success
from bettergit.core import gitio, branchmeta
from bettergit.core.gitio import GitError


def _style_branch(name: str, current: str, origins: dict[str, str]) -> str:
    if name == current:
        return typer.style(name, fg=typer.colors.BRIGHT_GREEN)
    if " -> " in name:
        return typer.style(name, fg=typer.colors.BRIGHT_MAGENTA)
    if name.startswith("remotes/"):
        return typer.style(name, fg=typer.colors.BRIGHT_CYAN)
    if name in origins:
        return typer.style(name, fg=typer.colors.BRIGHT_MAGENTA)
    return typer.style(name, fg=typer.colors.BRIGHT_BLUE)


def _category_header(title: str, note: str | None) -> str:
    return title if note is None else f"{title} {note}"


def register(app: typer.Typer) -> None:
    """Register the `bg branches` command."""

    @app.command("branches", help="Show a grouped, color-coded list of branches.")
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
        origins = branchmeta.load_all()

        current_lines: list[str] = []
        standalone_lines: list[str] = []
        derived_lines: list[str] = []
        remote_pointer_lines: list[str] = []
        remote_lines: list[str] = []
        derived_parents: set[str] = set()

        for name in items:
            prefix = "*" if name == current else " "
            display = _style_branch(name, current, origins)

            if name == current:
                prefix = typer.style(prefix, fg=typer.colors.BRIGHT_GREEN)
                current_lines.append(f"{prefix} {display}")
                continue

            if " -> " in name:
                remote_pointer_lines.append(f"{prefix} {display}")
                continue

            if name.startswith("remotes/"):
                remote_lines.append(f"{prefix} {display}")
                continue

            if name in origins:
                parent = origins.get(name)
                if parent:
                    derived_parents.add(parent)
                    parent_note = " " + typer.style(f"(from {parent})", fg=typer.colors.BRIGHT_BLACK)
                else:
                    parent_note = ""
                derived_lines.append(f"{prefix} {display}{parent_note}")
            else:
                standalone_lines.append(f"{prefix} {display}")

        categories: list[tuple[str, list[str], str | None]] = []
        categories.append(("Current Branch", current_lines, None))
        categories.append(("Individual branches", standalone_lines, None))

        derived_note: str | None = None
        if derived_parents:
            parents_list = ", ".join(sorted(derived_parents))
            derived_note = typer.style(f"(parents: {parents_list})", fg=typer.colors.BRIGHT_BLACK)
        categories.append(("Linked branches", derived_lines, derived_note))

        categories.append(("Remote HEAD Pointers", remote_pointer_lines, None))
        categories.append(("Remote Branches", remote_lines, None))

        typer.echo()
        printed_any = False
        for title, lines_chunk, note in categories:
            if not lines_chunk:
                continue
            if printed_any:
                typer.echo()
            header = _category_header(title, note)
            typer.secho(header, fg=typer.colors.BRIGHT_WHITE, bold=True)
            for line in lines_chunk:
                typer.echo(line)
            printed_any = True
