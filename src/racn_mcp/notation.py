"""Arlo's Risk-Aware Commit Notation: message formatting and validation."""

from __future__ import annotations

from typing import Literal

RISK_LEVELS: dict[str, str] = {
    ".": "Proven Safe",
    "^": "Validated",
    "!": "Risky",
    "@": "Probably Broken",
}

CORE_INTENTIONS: dict[str, str] = {
    "F": "Feature (behavior-changing / user-visible)",
    "f": "Feature",
    "B": "Bugfix (behavior-changing / user-visible)",
    "b": "Bugfix",
    "R": "Refactoring (behavior-changing / user-visible)",
    "r": "Refactoring",
    "D": "Documentation (behavior-changing / user-visible)",
    "d": "Documentation",
}

# Project-specific Extension Intentions, per
# https://github.com/RefactoringCombos/ArlosCommitNotation/blob/main/Extension%20Intentions.md
EXTENSION_INTENTIONS: dict[str, str] = {
    "M": "Merge (behavior-changing / user-visible)",
    "m": "Merge",
    "T": "Test-only (behavior-changing / user-visible)",
    "t": "Test-only",
    "E": "Environment (behavior-changing / user-visible)",
    "e": "Environment: non-code changes to dev setup/tooling that don't affect program behavior",
    "A": "Auto (behavior-changing / user-visible)",
    "a": "Auto: automatic formatting, code generation, or similar",
    "c": "Comment: changes comments only",
    "C": "Content: changes user-visible content (e.g. website copy)",
    "P": "Process (behavior-changing / user-visible)",
    "p": "Process: changes a team process or working agreement",
    "S": "Spec (behavior-changing / user-visible)",
    "s": "Spec: changes the spec or design",
    "N": "NOP (behavior-changing / user-visible)",
    "n": "NOP: a commit with no changes",
}

INTENTIONS: dict[str, str] = {**CORE_INTENTIONS, **EXTENSION_INTENTIONS}

# Named form of the risk levels above, for callers (e.g. LLMs) that reason
# more reliably about words than single-character RACN symbols.
RISK_NAMES: dict[str, str] = {
    "proven_safe": ".",
    "validated": "^",
    "risky": "!",
    "probably_broken": "@",
}

RiskName = Literal[tuple(RISK_NAMES)]


class NotationError(ValueError):
    """Raised when risk, intention, or comment fail validation."""


def resolve_risk_name(name: str) -> str:
    """Translate a named risk level (e.g. "risky") to its RACN symbol (e.g. "!")."""
    try:
        return RISK_NAMES[name]
    except KeyError:
        raise NotationError(
            f"Invalid risk {name!r}. Must be one of: {', '.join(RISK_NAMES)}"
        ) from None


def format_commit_message(risk: str, intention: str, comment: str) -> str:
    """Build a commit message in Arlo's Risk-Aware Commit Notation.

    Format: "<risk> <intention> <comment>", e.g. ". r Extract method".
    """
    if risk not in RISK_LEVELS:
        raise NotationError(
            f"Invalid risk {risk!r}. Must be one of: {', '.join(RISK_LEVELS)}"
        )
    if intention not in INTENTIONS:
        raise NotationError(
            f"Invalid intention {intention!r}. Must be one of: {', '.join(INTENTIONS)}"
        )
    comment = comment.strip()
    if not comment:
        raise NotationError("Comment must not be empty")

    return f"{risk} {intention} {comment}"
