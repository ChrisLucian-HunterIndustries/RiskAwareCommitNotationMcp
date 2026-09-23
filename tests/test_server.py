import subprocess
from pathlib import Path

import pytest

from racn_mcp.server import close_theme, commit, mcp, notation_reference


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
        location=str(repo),
        intention="refactoring",
        risk="proven_safe",
        comment="Add a.txt",
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
        commit(
            location=str(repo), intention="refactoring", risk="proven_safe", comment="x"
        )


def test_commit_tool_embeds_inline_theme_slug(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    result = commit(
        location=str(repo),
        intention="feature",
        risk="proven_safe",
        comment="Add validation",
        theme_slug="checkout-redesign",
        theme_mode="inline",
    )

    assert result.endswith(". f [checkout-redesign] Add validation")


def test_commit_tool_raises_value_error_for_mismatched_theme_args(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")

    with pytest.raises(ValueError, match="theme_slug and theme_mode"):
        commit(
            location=str(repo),
            intention="feature",
            risk="proven_safe",
            comment="x",
            theme_slug="checkout-redesign",
        )


def test_close_theme_tool_merges_theme_branch(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")
    commit(
        location=str(repo),
        intention="refactoring",
        risk="proven_safe",
        comment="Initial commit",
    )
    base_branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()

    (repo / "b.txt").write_text("world")
    _git(repo, "add", "b.txt")
    commit(
        location=str(repo),
        intention="feature",
        risk="proven_safe",
        comment="Add b.txt",
        theme_slug="checkout-redesign",
        theme_mode="d_shaped_merge",
    )

    result = close_theme(
        location=str(repo), slug="checkout-redesign", target_branch=base_branch
    )

    assert result.startswith("Merged theme 'checkout-redesign' into " + base_branch)
    log = subprocess.run(
        ["git", "log", "-1", "--pretty=%s"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    assert log.stdout.strip() == "checkout-redesign"


def test_close_theme_tool_raises_value_error_when_branch_missing(repo: Path):
    (repo / "a.txt").write_text("hello")
    _git(repo, "add", "a.txt")
    commit(
        location=str(repo),
        intention="refactoring",
        risk="proven_safe",
        comment="Initial commit",
    )

    with pytest.raises(ValueError, match="No theme branch"):
        close_theme(
            location=str(repo), slug="nonexistent-theme", target_branch="master"
        )


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


def test_server_instructions_call_for_small_commits():
    assert "small" in mcp.instructions
    assert "less clear commit history" in mcp.instructions
