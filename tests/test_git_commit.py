import subprocess
from pathlib import Path

import pytest

from racn_mcp.git_commit import CommitError, commit


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


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
        ["git", "log", "-1", "--pretty=%s"], cwd=repo, capture_output=True, text=True, check=True
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
