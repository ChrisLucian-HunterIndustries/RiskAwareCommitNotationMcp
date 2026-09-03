import subprocess
from pathlib import Path

import pytest

from racn_mcp.server import commit, mcp, notation_reference


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "test@example.com")
    _git(tmp_path, "config", "user.name", "Test")
    return tmp_path


def test_commit_tool_commits_staged_changes(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    result = commit(
        location=str(repo), intention="refactoring", risk="proven_safe", comment="Add a.txt"
    )

    assert result.startswith("Committed ")
    assert result.endswith(". r Add a.txt")
    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    assert log.stdout.strip() == ". r Add a.txt"


def test_commit_tool_raises_value_error_for_invalid_risk(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    with pytest.raises(ValueError, match="Invalid risk"):
        commit(location=str(repo), intention="refactoring", risk="unknown", comment="x")


def test_commit_tool_raises_value_error_when_nothing_staged(repo: Path):
    with pytest.raises(ValueError, match="No staged changes"):
        commit(location=str(repo), intention="refactoring", risk="proven_safe", comment="x")


def test_notation_reference_lists_risk_levels_and_intentions():
    text = notation_reference()

    assert "Risk levels:" in text
    assert "Intentions:" in text
    assert "proven_safe  Proven Safe" in text
    assert "feature  Feature" in text


def test_server_instructions_explain_racn_usage():
    assert mcp.instructions is not None
    assert "Risk-Aware Commit Notation" in mcp.instructions
    assert "notation_reference" in mcp.instructions
    assert "commit" in mcp.instructions
