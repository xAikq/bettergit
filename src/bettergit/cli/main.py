from __future__ import annotations

import textwrap

import typer
from typer.core import TyperGroup

from bettergit import __version__

import importlib
import bettergit.cli.commands as commands
import pkgutil


HELP_TEXT = textwrap.dedent(
    """
    +======================================================================+
    | BetterGit CLI (bg)                                                   |
    +======================================================================+

    Usage
      bg [GLOBAL OPTIONS] COMMAND [ARGS...]

    Global Options
      -h, --help            Show this message and exit.
      -V, --version         Print the installed BetterGit version and exit.
      -c, --config PATH     Override the config file for commands that accept it.

    ----------------------------------------------------------------------
    Workflow
      1) Stage changes        -> bg add [PATHS...]
      2) Craft a message      -> bg suggest (interactive) | bg commit
      3) Publish your work    -> bg push (current) | bg push-to <branch>

    ----------------------------------------------------------------------
    Staging & Commits
      bg add            Stage everything (no args) or selected paths.
      bg suggest        Interactive commit assistant.
      bg commit         Fire-and-forget Conventional Commit generator.

    ----------------------------------------------------------------------
    Branch Management
      bg branch         Grouped, color-coded view for current, standalone, derived, 
                          and remote branches (add --all/-a for remotes).
      bg branch-info    Ahead/behind stats, tracking target, last commit snapshot.
      bg switch         Checkout another branch.
      bg create-branch  Start from HEAD by default; can switch automatically.
      bg delete-branch  Drop local branch, optionally clean remote copy.

    ----------------------------------------------------------------------
    Sync & Sharing
      bg push           Push current or specific branch.
      bg push-to        Push any branch without switching.

    ----------------------------------------------------------------------
    Examples
      bg add src/bettergit/core/gitio.py
      bg suggest --llm
      bg create-branch feature/payments --from main
      bg delete-branch feature/payments --remote-delete
      bg push --branch feature/payments --remote origin
      bg push-to release/v1.0 --remote upstream

    ----------------------------------------------------------------------
    Pro Tips
      * Most commands honor --config/-c for per-run overrides.
      * Force flags map directly to git; use them carefully.
      * BetterGit surfaces git's stderr verbatim, so errors stay familiar.
      * Run `bg COMMAND --help` for command-specific switches.

    +======================================================================+
    """
)


class BetterGitGroup(TyperGroup):
    """Custom Typer group that prints a structured help banner."""

    def format_help(self, ctx, formatter) -> None:  # type: ignore[override]
        formatter.write(HELP_TEXT)
        formatter.write("\n\nCommands\n")
        commands_list: list[tuple[str, str]] = []
        for name in self.list_commands(ctx):
            command = self.get_command(ctx, name)
            if command is None:
                continue
            commands_list.append((name, command.get_short_help_str()))
        if commands_list:
            width = max(len(name) for name, _ in commands_list)
            for name, help_str in commands_list:
                formatter.write(f"  {name.ljust(width)}  {help_str}\n")
        else:
            formatter.write("  (no commands registered)\n")
        formatter.write("\nOptions\n")
        formatter.write("  -h, --help      Show this message and exit.\n")
        formatter.write("  -V, --version   Show the BetterGit version and exit.\n")


app = typer.Typer(
    add_completion=False,
    cls=BetterGitGroup,
    context_settings={"help_option_names": ["-h", "--help"], "max_content_width": 110},
)


@app.callback(invoke_without_command=True)
def main(
        ctx: typer.Context,
        version: bool = typer.Option(
            False,
            "--version",
            "-V",
            help="Show the BetterGit version and exit.",
            is_eager=True,
        ),
) -> None:
    """Top-level callback that powers global flags like --version."""

    if version:
        typer.echo(f"BetterGit {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None and not ctx.resilient_parsing:
        typer.echo(ctx.get_help())
        raise typer.Exit()


for importer, module_name, is_pkg in pkgutil.iter_modules(commands.__path__):
    full_module_name = f"bettergit.cli.commands.{module_name}"
    module = importlib.import_module(full_module_name)
    if hasattr(module, 'register'):
        module.register(app)


def run() -> None:
    app()


if __name__ == "__main__":
    run()
