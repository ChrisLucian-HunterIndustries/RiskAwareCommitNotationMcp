"""MCP server exposing a `commit` tool for Arlo's Risk-Aware Commit Notation."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from racn_mcp.git_commit import CommitError, commit as do_commit
from racn_mcp.notation import INTENTIONS, RISK_LEVELS

mcp = MCPServer(
    "risk-aware-commit-notation",
    instructions=(
        "Commits changes to a Git repository using Arlo's Risk-Aware Commit "
        "Notation (RACN). RACN messages take the form "
        '"<risk> <intention> <comment>", encoding how risky a change is and '
        "what the author intended alongside the summary. Call "
        "`notation_reference` to look up the valid risk levels and intentions "
        "(including Extension Intentions) before classifying a change, then "
        "call `commit` with the classification. Stage changes with `git add` "
        "first; this server does not stage them for you."
    ),
)


@mcp.tool()
def commit(location: str, intention: str, risk: str, comment: str) -> str:
    """Commit staged changes in a Git repository using Arlo's Risk-Aware Commit Notation.

    The resulting commit message has the form "<risk> <intention> <comment>".
    Assumes changes are already staged (`git add`) at `location`.

    Args:
        location: Path to the Git repository (or a directory inside it).
        intention: One of F/f (Feature), B/b (Bugfix), R/r (Refactoring), D/d (Documentation).
        risk: One of . (Proven Safe), ^ (Validated), ! (Risky), @ (Probably Broken).
        comment: The commit summary text.
    """
    try:
        result = do_commit(
            location=location, intention=intention, risk=risk, comment=comment
        )
    except CommitError as e:
        raise ValueError(str(e)) from e

    return f"Committed {result.commit_hash[:12]}: {result.message}"


@mcp.tool()
def notation_reference() -> str:
    """Return the risk levels and intentions available in Arlo's Risk-Aware Commit Notation."""
    risk_lines = "\n".join(f"  {code}  {name}" for code, name in RISK_LEVELS.items())
    intention_lines = "\n".join(
        f"  {code}  {name}" for code, name in INTENTIONS.items()
    )
    return f"Risk levels:\n{risk_lines}\n\nIntentions:\n{intention_lines}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
