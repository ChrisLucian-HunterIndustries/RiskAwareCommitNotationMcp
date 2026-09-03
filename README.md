# Risk-Aware Commit Notation MCP Server

An MCP server that commits staged changes to a Git repository using
[Arlo's Risk-Aware Commit Notation](https://github.com/RefactoringCombos/ArlosCommitNotation)
(RACN).

RACN encodes two pieces of metadata in the first characters of a commit
message: how risky the change is, and what the author intended. This server
builds and applies commit messages in that format instead of leaving it to
the caller to remember the syntax.

## What it does

The server exposes two MCP tools:

- **`commit`** — commits the currently staged changes in a Git repository
  using a RACN-formatted message (`"<risk> <intention> <comment>"`, e.g.
  `. r Extract method`). It does **not** stage changes for you; run `git add`
  first.
- **`notation_reference`** — returns the full list of valid risk levels and
  intentions (including project Extension Intentions), for a client to look
  up before calling `commit`.

The JSON manifest a consuming MCP client reads for these tools (names,
descriptions, and input/output schemas) is captured in
[`tests/manifest.approved.json`](tests/manifest.approved.json).

### `commit` parameters

| Parameter   | Description                                                                 |
|-------------|-------------------------------------------------------------------------------|
| `location`  | Path to the Git repository (or a directory inside it).                        |
| `risk`      | One of `proven_safe`, `validated`, `risky`, `probably_broken`.                |
| `intention` | A core intention (`feature`, `bugfix`, `refactoring`, `documentation`) or an Extension Intention (`environment`, `test_only`, `merge`, `auto`, `comment`, `content`, `process`, `spec`, `nop`), each with a `_user_visible` variant (e.g. `feature_user_visible`) for a behavior-changing / user-visible change. |
| `comment`   | The commit summary text.                                                      |

`risk` and `intention` are named values rather than the raw RACN symbols so
a caller doesn't have to memorize single-character codes; the server
translates them to the symbol before building the commit message. Call
`notation_reference` for the full list and what each means. See the
[RACN README](https://github.com/RefactoringCombos/ArlosCommitNotation)
and [Extension Intentions](https://github.com/RefactoringCombos/ArlosCommitNotation/blob/main/Extension%20Intentions.md)
docs for the underlying notation.

## Running the server

```sh
mise run run
```

This starts the server on stdio, ready to be connected to by an MCP client
(e.g. registered as a tool provider in an AI coding assistant).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for dev setup and development notes.
