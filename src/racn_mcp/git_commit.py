"""Committing to a Git repository using Arlo's Risk-Aware Commit Notation."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from racn_mcp.notation import (
    THEME_MODES,
    NotationError,
    ThemeMode,
    format_commit_message,
    validate_theme_slug,
)


class CommitError(RuntimeError):
    """Raised when the commit cannot be performed."""


@dataclass
class CommitResult:
    commit_hash: str
    message: str


def commit(
    location: str,
    intention: str,
    risk: str,
    comment: str,
    theme_slug: str | None = None,
    theme_mode: ThemeMode | None = None,
) -> CommitResult:
    """Commit currently-staged changes in `location` using the given notation.

    Assumes the caller has already staged (`git add`) whatever should be committed.

    `theme_slug` and `theme_mode` must be given together (or not at all) to
    group this commit under a feature theme. In "inline" mode the slug is
    embedded in this commit's message. In "d_shaped_merge" mode this commit
    is made on a branch named after the slug (created from the current HEAD
    if it doesn't already exist) instead of the current branch; use
    `close_theme` afterwards to merge that branch back.
    """
    repo_path = Path(location)
    if not repo_path.is_dir():
        raise CommitError(f"Location does not exist or is not a directory: {location}")

    if (theme_slug is None) != (theme_mode is None):
        raise CommitError("theme_slug and theme_mode must be given together")
    if theme_mode is not None and theme_mode not in THEME_MODES:
        raise CommitError(
            f"Invalid theme mode {theme_mode!r}. Must be one of: {', '.join(THEME_MODES)}"
        )

    try:
        if theme_slug is not None:
            validate_theme_slug(theme_slug)
        if theme_mode == "inline":
            message = format_commit_message(risk, intention, comment, theme_slug)
        else:
            message = format_commit_message(risk, intention, comment)
    except NotationError as e:
        raise CommitError(str(e)) from e

    _run_git(repo_path, ["rev-parse", "--is-inside-work-tree"])

    staged = _run_git(repo_path, ["diff", "--cached", "--name-only"]).stdout.strip()
    if not staged:
        raise CommitError("No staged changes to commit in " + str(repo_path))

    if theme_mode == "d_shaped_merge":
        assert theme_slug is not None
        if not _branch_exists(repo_path, theme_slug):
            _run_git(repo_path, ["branch", theme_slug])
        _run_git(repo_path, ["checkout", theme_slug])

    _run_git(repo_path, ["commit", "-m", message])
    commit_hash = _run_git(repo_path, ["rev-parse", "HEAD"]).stdout.strip()

    return CommitResult(commit_hash=commit_hash, message=message)


def close_theme(location: str, slug: str, target_branch: str) -> CommitResult:
    """Merge a "d_shaped_merge" theme's branch back into `target_branch`.

    Merges non-fast-forward (`git merge --no-ff`) so the theme's commits stay
    grouped under a single merge commit, using `slug` as its message.
    """
    repo_path = Path(location)
    if not repo_path.is_dir():
        raise CommitError(f"Location does not exist or is not a directory: {location}")

    try:
        validate_theme_slug(slug)
    except NotationError as e:
        raise CommitError(str(e)) from e

    _run_git(repo_path, ["rev-parse", "--is-inside-work-tree"])

    if not _branch_exists(repo_path, slug):
        raise CommitError(f"No theme branch named {slug!r} found in {repo_path}")

    _run_git(repo_path, ["checkout", target_branch])
    _run_git(repo_path, ["merge", "--no-ff", slug, "-m", slug])
    commit_hash = _run_git(repo_path, ["rev-parse", "HEAD"]).stdout.strip()

    return CommitResult(commit_hash=commit_hash, message=slug)


def _branch_exists(repo_path: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
        cwd=repo_path,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


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
