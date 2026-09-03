import pytest

from racn_mcp.notation import NotationError, format_commit_message


def test_formats_message_with_risk_intention_and_comment():
    assert format_commit_message(".", "r", "Extract method") == ". r Extract method"


def test_formats_broken_risk_example():
    assert (
        format_commit_message("@", "r", "Start extracting method with no name")
        == "@ r Start extracting method with no name"
    )


@pytest.mark.parametrize("risk", [".", "^", "!", "@"])
def test_accepts_all_risk_levels(risk):
    assert format_commit_message(risk, "f", "x").startswith(risk)


@pytest.mark.parametrize("intention", ["F", "f", "B", "b", "R", "r", "D", "d"])
def test_accepts_all_core_intentions(intention):
    assert format_commit_message(".", intention, "x") == f". {intention} x"


@pytest.mark.parametrize(
    "intention", ["M", "m", "T", "t", "E", "e", "A", "a", "c", "C", "P", "p", "S", "s", "N", "n"]
)
def test_accepts_all_extension_intentions(intention):
    assert format_commit_message(".", intention, "x") == f". {intention} x"


def test_environment_extension_intention_for_tooling_changes():
    assert format_commit_message(".", "e", "Add .gitignore") == ". e Add .gitignore"


def test_rejects_invalid_risk():
    with pytest.raises(NotationError):
        format_commit_message("?", "f", "x")


def test_rejects_invalid_intention():
    with pytest.raises(NotationError):
        format_commit_message(".", "x", "x")


def test_rejects_empty_comment():
    with pytest.raises(NotationError):
        format_commit_message(".", "f", "   ")
