# Risk-Aware Commit Notation MCP Server

An MCP server that commits staged changes to a Git repository using
[Arlo's Risk-Aware Commit Notation](https://github.com/RefactoringCombos/ArlosCommitNotation)
(RACN).

RACN encodes two pieces of metadata in the first characters of a commit
message: how risky the change is, and what the author intended. This server
builds and applies commit messages in that format instead of leaving it to
the caller to remember the syntax.

## What it does

The server exposes three MCP tools:

- **`commit`** — commits the currently staged changes in a Git repository
  using a RACN-formatted message (`"<risk> <intention> <comment>"`, e.g.
  `. r Extract method`). It does **not** stage changes for you; run `git add`
  first. Optionally pass `theme_slug` and `theme_mode` to group several
  commits under a feature theme — see [Grouping commits under a feature
  theme](#grouping-commits-under-a-feature-theme) below.
- **`close_theme`** — merges a `d_shaped_merge` theme's branch back into a
  target branch, non-fast-forward, with the theme's slug as the merge
  commit's message.
- **`notation_reference`** — returns the full list of valid risk levels and
  intentions (including project Extension Intentions), for a client to look
  up before calling `commit`.

The JSON manifest a consuming MCP client reads for these tools (names,
descriptions, and input/output schemas) is captured in
[`tests/manifest.approved.json`](tests/manifest.approved.json).

### `commit` parameters

| Parameter    | Description                                                                 |
|--------------|-------------------------------------------------------------------------------|
| `location`   | Path to the Git repository (or a directory inside it).                        |
| `risk`       | One of `proven_safe`, `validated`, `risky`, `probably_broken`.                |
| `intention`  | A core intention (`feature`, `bugfix`, `refactoring`, `documentation`) or an Extension Intention (`environment`, `test_only`, `merge`, `auto`, `comment`, `content`, `process`, `spec`, `nop`), each with a `_user_visible` variant (e.g. `feature_user_visible`) for a behavior-changing / user-visible change. |
| `comment`    | The commit summary text.                                                      |
| `theme_slug` | Optional feature theme slug (lowercase, hyphenated, e.g. `checkout-redesign`) grouping this commit with others. Must be given together with `theme_mode`. |
| `theme_mode` | Optional; either `inline` or `d_shaped_merge`. Required together with `theme_slug`. |

`risk` and `intention` are named values rather than the raw RACN symbols so
a caller doesn't have to memorize single-character codes; the server
translates them to the symbol before building the commit message. Call
`notation_reference` for the full list and what each means. See the
[RACN README](https://github.com/RefactoringCombos/ArlosCommitNotation)
and [Extension Intentions](https://github.com/RefactoringCombos/ArlosCommitNotation/blob/main/Extension%20Intentions.md)
docs for the underlying notation.

### Grouping commits under a feature theme

Pass `theme_slug` and `theme_mode` to `commit` to mark several commits as
belonging to the same feature theme:

- **`inline`** — the slug is embedded in each commit's message, e.g.
  `. f [checkout-redesign] Add validation`. Commits stay on the current
  branch.
- **`d_shaped_merge`** — each commit is made on a branch named after the
  slug instead of the current branch (created from the current HEAD the
  first time the slug is used). Once all of a theme's commits are made,
  call **`close_theme`** with the same slug and a `target_branch` to merge
  that branch back non-fast-forward (`git merge --no-ff`), using the slug as
  the merge commit's message — grouping the theme's commits under a single
  "D"-shaped merge in the history.

## Running the server

Requires [mise](https://mise.jdx.dev/) — it installs the pinned Python and
uv for you, so no other setup is needed.

<!-- snippet: running-the-server.sh -->
<a id='snippet-running-the-server.sh'></a>
```sh
git clone https://github.com/JayBazuzi/RiskAwareCommitNotationMcp.git
cd RiskAwareCommitNotationMcp
mise run run
```
<sup><a href='/docs/running-the-server.sh#L1-L3' title='Snippet source file'>snippet source</a> | <a href='#snippet-running-the-server.sh' title='Start of snippet'>anchor</a></sup>
<!-- endSnippet -->

`mise run run` installs Python/uv and dependencies on first use, then starts
the server on stdio, ready to be connected to by an MCP client (e.g.
registered as a tool provider in an AI coding assistant).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for dev setup and development notes.
