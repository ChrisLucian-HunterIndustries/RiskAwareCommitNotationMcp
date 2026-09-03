"""Committing to a Git repository using Arlo's Risk-Aware Commit Notation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from racn_mcp.notation import NotationError, format_commit_message


class CommitError(RuntimeError):
    """Raised when the commit cannot be performed."""


@dataclass
class CommitResult:
    commit_hash: str
    message: str


def commit(location: str, intention: str, risk: str, comment: str) -> CommitResult:
    """Commit currently-staged changes in `location` using the given notation.

    Assumes the caller has already staged (`git add`) whatever should be committed.
    """
    repo_path = Path(location)
    if not repo_path.is_dir():
        raise CommitError(f"Location does not exist or is not a directory: {location}")

    try:
        message = format_commit_message(risk, intention, comment)
    except NotationError as e:
        raise CommitError(str(e)) from e

    _run_git(repo_path, ["rev-parse", "--is-inside-work-tree"])

    staged = _run_git(repo_path, ["diff", "--cached", "--name-only"]).stdout.strip()
    if not staged:
        raise CommitError("No staged changes to commit in " + str(repo_path))

    _run_git(repo_path, ["commit", "-m", message])
    commit_hash = _run_git(repo_path, ["rev-parse", "HEAD"]).stdout.strip()

    return CommitResult(commit_hash=commit_hash, message=message)


def _run_git(cwd: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CommitError(
            f"git {' '.join(args)} failed: {result.stderr.strip() or result.stdout.strip()}"
        )
    return result
