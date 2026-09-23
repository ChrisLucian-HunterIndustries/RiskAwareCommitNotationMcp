"""MCP server exposing a `commit` tool for Arlo's Risk-Aware Commit Notation."""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from racn_mcp.git_commit import CommitError
from racn_mcp.git_commit import close_theme as do_close_theme
from racn_mcp.git_commit import commit as do_commit
from racn_mcp.notation import (
    INTENTION_NAMES,
    INTENTIONS,
    RISK_LEVELS,
    RISK_NAMES,
    IntentionName,
    NotationError,
    RiskName,
    ThemeMode,
    resolve_intention_name,
    resolve_risk_name,
)

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
        "first; this server does not stage them for you. This tool is "
        "intended to be used with very small, focused commits: stage and "
        "commit one distinct concern at a time rather than batching several "
        "into one call. Skipping small commits in favor of large ones "
        "produces a less clear commit history. To group several related "
        "commits under a feature theme, pass a `theme_slug` and `theme_mode` "
        "to `commit`; for `theme_mode='d_shaped_merge'`, call `close_theme` "
        "once the theme's commits are done."
    ),
)


@mcp.tool()
def commit(
    location: str,
    intention: IntentionName,
    risk: RiskName,
    comment: str,
    theme_slug: str | None = None,
    theme_mode: ThemeMode | None = None,
) -> str:
    """Commit staged changes in a Git repository using Arlo's Risk-Aware Commit Notation.

    The resulting commit message has the form "<risk> <intention> <comment>",
    e.g. ". test_only Add approval test". Call `notation_reference` first to
    see the full list of intentions and risk levels and what each means.
    Assumes changes are already staged (`git add`) at `location`.

    Pass `theme_slug` and `theme_mode` together to group this commit with
    others under a feature theme (a lowercase, hyphenated slug, e.g.
    "checkout-redesign"):

    - `theme_mode="inline"`: the slug is embedded in this commit's message,
      e.g. ". f [checkout-redesign] Add validation".
    - `theme_mode="d_shaped_merge"`: this commit is made on a branch named
      after the slug (created from the current HEAD the first time it's
      used) instead of the current branch. Call `close_theme` afterwards to
      merge that branch back with `slug` as the merge commit's message,
      forming a "D" shape in the history.

    Args:
        location: Path to the Git repository (or a directory inside it).
        intention: The author's intention for the change, e.g. "feature" or "test_only".
        risk: How risky the change is, e.g. "proven_safe" or "risky".
        comment: The commit summary text.
        theme_slug: Feature theme slug to group this commit under, if any.
        theme_mode: How to group commits under `theme_slug`: "inline" or "d_shaped_merge".
    """
    try:
        symbolic_risk = resolve_risk_name(risk)
        symbolic_intention = resolve_intention_name(intention)
        result = do_commit(
            location=location,
            intention=symbolic_intention,
            risk=symbolic_risk,
            comment=comment,
            theme_slug=theme_slug,
            theme_mode=theme_mode,
        )
    except (NotationError, CommitError) as e:
        raise ValueError(str(e)) from e

    return f"Committed {result.commit_hash[:12]}: {result.message}"


@mcp.tool()
def close_theme(location: str, slug: str, target_branch: str) -> str:
    """Merge a "d_shaped_merge" feature theme's branch back into `target_branch`.

    Merges non-fast-forward (`git merge --no-ff`) so the theme's commits
    stay grouped under a single merge commit on top of `target_branch`, using
    `slug` as that merge commit's message. Call this once all of a theme's
    `commit(..., theme_mode="d_shaped_merge")` calls are done.

    Args:
        location: Path to the Git repository (or a directory inside it).
        slug: The feature theme slug previously passed to `commit` as `theme_slug`.
        target_branch: The branch to merge the theme's branch into.
    """
    try:
        result = do_close_theme(
            location=location, slug=slug, target_branch=target_branch
        )
    except (NotationError, CommitError) as e:
        raise ValueError(str(e)) from e

    return f"Merged theme {slug!r} into {target_branch} as {result.commit_hash[:12]}"


@mcp.tool()
def notation_reference() -> str:
    """Return the risk levels and intentions available in Arlo's Risk-Aware Commit Notation."""
    risk_lines = "\n".join(
        f"  {name}  {RISK_LEVELS[symbol]}" for name, symbol in RISK_NAMES.items()
    )
    intention_lines = "\n".join(
        f"  {name}  {INTENTIONS[symbol]}" for name, symbol in INTENTION_NAMES.items()
    )
    return f"Risk levels:\n{risk_lines}\n\nIntentions:\n{intention_lines}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
