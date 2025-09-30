from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence
import subprocess

__all__ = [
    "GitError",
    "BranchInfo",
    "add",
    "add_all",
    "branch_info",
    "checkout",
    "commit",
    "create_branch",
    "current_branch",
    "delete_branch",
    "delete_remote_branch",
    "get_changed_files",
    "get_staged_diff",
    "has_upstream",
    "list_branches",
    "push",
    "remote_branch_exists",
    "tag",
    "crete_tag",
    "delete_tag",
]

_GIT_PREFIX: list[str] = [
    "git",
    "-c",
    "core.quotepath=false",
    "-c",
    "i18n.logOutputEncoding=utf-8",
]


class GitError(RuntimeError):
    """Raised when a git command exits with a non-zero status."""


def _run_git(args: Sequence[str]) -> str:
    process = subprocess.run(
        [*_GIT_PREFIX, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if process.returncode != 0:
        stdout = process.stdout.strip()
        stderr = process.stderr.strip()
        message = "\n".join(filter(None, (stdout, stderr)))
        command_str = " ".join([*_GIT_PREFIX, *args])
        raise GitError(message or f"git failed: {command_str}")
    return process.stdout.strip()


def get_staged_diff() -> str:
    """Return the unified diff for staged changes."""

    return _run_git(["diff", "--cached", "--no-color"])


def get_changed_files() -> list[str]:
    """Return the list of staged files."""

    output = _run_git(["diff", "--cached", "--name-only", "--no-color"])
    return [line for line in output.splitlines() if line]


def commit(message: str) -> None:
    """Create a commit with *message*."""

    _run_git(["commit", "-m", message])


def add_all() -> None:
    """Stage all tracked changes."""

    _run_git(["add", "-A"])


def add(paths: Sequence[str]) -> None:
    """Stage the given *paths*."""

    _run_git(["add", "--", *paths])


def current_branch() -> str:
    """Return the name of the current branch."""

    return _run_git(["rev-parse", "--abbrev-ref", "HEAD"])


def create_branch(
    branch_name: str,
    start_point: str | None = None,
    checkout: bool = True,
    force: bool = False,
) -> None:
    """Create *branch_name* from *start_point* and optionally switch to it."""

    if checkout:
        switch_flag = "-C" if force else "-c"
        args = ["switch", switch_flag, branch_name]
    else:
        args = ["branch"]
        if force:
            args.append("-f")
        args.append(branch_name)
    if start_point:
        args.append(start_point)
    _run_git(args)


def delete_branch(branch_name: str, force: bool = False) -> None:
    """Delete a local branch."""

    flag = "-D" if force else "-d"
    _run_git(["branch", flag, branch_name])


def delete_remote_branch(remote: str, branch: str) -> None:
    """Delete *branch* on *remote*."""

    _run_git(["push", remote, "--delete", branch])


@dataclass(frozen=True)
class BranchInfo:
    """Collected metadata about a git branch."""

    name: str
    tracking: str | None
    ahead: int
    behind: int
    last_commit_sha: str | None
    last_commit_author: str | None
    last_commit_date: str | None
    last_commit_title: str | None


def list_branches(all_: bool = False) -> list[str]:
    """Return the list of branch names."""

    args: list[str] = ["branch"]
    if all_:
        args.append("--all")
    output = _run_git(args)
    names: list[str] = []
    for raw in output.splitlines():
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("* "):
            stripped = stripped[2:]
        names.append(stripped)
    return names


def checkout(branch: str) -> None:
    """Switch HEAD to *branch*."""

    _run_git(["checkout", branch])


def branch_info(branch: str | None = None) -> BranchInfo:
    """Return information about *branch* (defaults to the current branch)."""

    branch_name = branch or current_branch()
    try:
        tracking = _run_git(["rev-parse", "--abbrev-ref", f"{branch_name}@{{upstream}}"])
    except GitError:
        tracking = None

    ahead = behind = 0
    if tracking:
        counts = _run_git(["rev-list", "--left-right", "--count", f"{tracking}...{branch_name}"])
        left, right = counts.replace("\t", " ").split()
        ahead = int(right)
        behind = int(left)

    last_commit_sha = last_commit_author = last_commit_date = last_commit_title = None
    if list_branches():
        pretty = "%H%x1f%an%x1f%ad%x1f%s"
        data = _run_git(["log", "-1", f"--pretty=format:{pretty}", branch_name])
        if data:
            parts = data.split("\x1f")
            if len(parts) == 4:
                last_commit_sha, last_commit_author, last_commit_date, last_commit_title = parts

    return BranchInfo(
        name=branch_name,
        tracking=tracking,
        ahead=ahead,
        behind=behind,
        last_commit_sha=last_commit_sha or None,
        last_commit_author=last_commit_author or None,
        last_commit_date=last_commit_date or None,
        last_commit_title=last_commit_title or None,
    )


def has_upstream(branch: str | None = None) -> bool:
    """Return True if *branch* has an upstream configured."""

    branch_name = branch or current_branch()
    try:
        _run_git(["rev-parse", "--abbrev-ref", f"{branch_name}@{{upstream}}"])
    except GitError:
        return False
    return True


def push(remote: str = "origin", branch: str | None = None, set_upstream: bool = True) -> bool:
    """Push *branch* to *remote*.

    Returns True if the command had to set the upstream reference.
    """

    ref = branch or current_branch()
    needs_upstream = set_upstream and not has_upstream(ref)
    args: list[str] = ["push"]
    if needs_upstream:
        args.append("-u")
    args.extend([remote, ref])
    _run_git(args)
    return needs_upstream



def remote_branch_exists(remote: str = "origin", branch: str | None = None) -> bool:
    """Return True if *branch* exists on *remote*."""

    ref = branch or current_branch()
    output = _run_git(["ls-remote", "--heads", remote, ref])
    return bool(output.strip())


def tag() -> str:
    """Shows all tags."""

    output = _run_git(["tag"])
    return output


def create_tag(name: str, message: str | None = None) -> None:
    """Create tag with a given name, optionally with message."""

    if message is not None:
        _run_git(["tag", "-a", name, "-m", message])
    else:
        _run_git(["tag", name])


def delete_tag(name: str) -> None:
    """Delete tag."""

    _run_git(["tag", "-d", name])