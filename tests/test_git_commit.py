import subprocess
from pathlib import Path

import pytest

from racn_mcp.git_commit import CommitError, close_theme, commit


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _current_branch(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _commit_subjects(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "log", "--pretty=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip().splitlines()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    return tmp_path


def test_commits_staged_changes(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    result = commit(location=str(repo), intention="r", risk=".", comment="Add a.txt")

    assert result.message == ". r Add a.txt"
    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    assert log.stdout.strip() == ". r Add a.txt"


def test_raises_when_nothing_staged(repo: Path):
    with pytest.raises(CommitError, match="No staged changes"):
        commit(location=str(repo), intention="r", risk=".", comment="Nothing to do")


def test_raises_for_invalid_location():
    with pytest.raises(CommitError, match="does not exist"):
        commit(location="/does/not/exist", intention="r", risk=".", comment="x")


def test_raises_for_invalid_risk(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    with pytest.raises(CommitError, match="Invalid risk"):
        commit(location=str(repo), intention="r", risk="?", comment="x")


def test_raises_for_non_git_directory(tmp_path: Path):
    with pytest.raises(CommitError):
        commit(location=str(tmp_path), intention="r", risk=".", comment="x")


def test_inline_theme_embeds_slug_and_stays_on_current_branch(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    result = commit(
        location=str(repo),
        intention="f",
        risk=".",
        comment="Add validation",
        theme_slug="checkout-redesign",
        theme_mode="inline",
    )

    assert result.message == ". f [checkout-redesign] Add validation"
    assert _current_branch(repo) == "master" or _current_branch(repo) == "main"


def test_d_shaped_merge_theme_commits_to_branch_named_after_slug(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")
    commit(location=str(repo), intention="r", risk=".", comment="Initial commit")
    base_branch = _current_branch(repo)

    (repo / "b.txt").write_text("world")
    _git(repo, "add", "b.txt")
    result = commit(
        location=str(repo),
        intention="f",
        risk=".",
        comment="Add b.txt",
        theme_slug="checkout-redesign",
        theme_mode="d_shaped_merge",
    )

    assert result.message == ". f Add b.txt"
    assert _current_branch(repo) == "checkout-redesign"

    (repo / "c.txt").write_text("!")
    _git(repo, "add", "c.txt")
    commit(
        location=str(repo),
        intention="f",
        risk=".",
        comment="Add c.txt",
        theme_slug="checkout-redesign",
        theme_mode="d_shaped_merge",
    )

    assert _current_branch(repo) == "checkout-redesign"
    assert _commit_subjects(repo) == [
        ". f Add c.txt",
        ". f Add b.txt",
        ". r Initial commit",
    ]

    close_theme(location=str(repo), slug="checkout-redesign", target_branch=base_branch)

    assert _current_branch(repo) == base_branch
    subjects = _commit_subjects(repo)
    assert subjects[0] == "checkout-redesign"
    parents = subprocess.run(
        ["git", "rev-list", "--parents", "-1", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    assert len(parents) == 3  # commit hash + 2 parents


def test_raises_when_theme_slug_given_without_theme_mode(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    with pytest.raises(CommitError, match="theme_slug and theme_mode"):
        commit(
            location=str(repo),
            intention="r",
            risk=".",
            comment="x",
            theme_slug="checkout-redesign",
        )


def test_raises_when_theme_mode_given_without_theme_slug(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    with pytest.raises(CommitError, match="theme_slug and theme_mode"):
        commit(
            location=str(repo),
            intention="r",
            risk=".",
            comment="x",
            theme_mode="inline",
        )


def test_raises_for_invalid_theme_slug(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    with pytest.raises(CommitError, match="Invalid theme slug"):
        commit(
            location=str(repo),
            intention="r",
            risk=".",
            comment="x",
            theme_slug="Not A Slug",
            theme_mode="inline",
        )


def test_close_theme_raises_when_branch_does_not_exist(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")
    commit(location=str(repo), intention="r", risk=".", comment="Initial commit")

    with pytest.raises(CommitError, match="No theme branch"):
        close_theme(
            location=str(repo), slug="nonexistent-theme", target_branch="master"
        )


def test_close_theme_raises_for_invalid_location():
    with pytest.raises(CommitError, match="does not exist"):
        close_theme(
            location="/does/not/exist", slug="checkout-redesign", target_branch="main"
        )
