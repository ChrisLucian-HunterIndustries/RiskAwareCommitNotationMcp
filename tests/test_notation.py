import pytest

from racn_mcp.notation import (
    INTENTION_NAMES,
    RISK_NAMES,
    NotationError,
    format_commit_message,
    resolve_intention_name,
    resolve_risk_name,
)


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
    "intention",
    ["M", "m", "T", "t", "E", "e", "A", "a", "c", "C", "P", "p", "S", "s", "N", "n"],
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


@pytest.mark.parametrize(("name", "symbol"), RISK_NAMES.items())
def test_resolve_risk_name_maps_every_name_to_its_symbol(name, symbol):
    assert resolve_risk_name(name) == symbol


def test_resolve_risk_name_rejects_unknown_name():
    with pytest.raises(NotationError, match="Invalid risk"):
        resolve_risk_name("unknown")


@pytest.mark.parametrize(("name", "symbol"), INTENTION_NAMES.items())
def test_resolve_intention_name_maps_every_name_to_its_symbol(name, symbol):
    assert resolve_intention_name(name) == symbol


def test_resolve_intention_name_rejects_unknown_name():
    with pytest.raises(NotationError, match="Invalid intention"):
        resolve_intention_name("unknown")
