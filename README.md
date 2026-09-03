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
[`tests/test_manifest.test_tools_manifest.approved.json`](tests/test_manifest.test_tools_manifest.approved.json).

### `commit` parameters

| Parameter   | Description                                                                 |
|-------------|-------------------------------------------------------------------------------|
| `location`  | Path to the Git repository (or a directory inside it).                        |
| `risk`      | One of `.` (Proven Safe), `^` (Validated), `!` (Risky), `@` (Probably Broken). |
| `intention` | A core intention (`F`/`f`, `B`/`b`, `R`/`r`, `D`/`d`) or an Extension Intention (`e`, `t`, `m`, `a`, `c`, `C`, `p`, `s`, `n`, and uppercase variants). |
| `comment`   | The commit summary text.                                                      |

Casing on the intention letter follows your team's convention (e.g.
uppercase = user-visible / intended behavior change, lowercase = internal).
See the [RACN README](https://github.com/RefactoringCombos/ArlosCommitNotation)
and [Extension Intentions](https://github.com/RefactoringCombos/ArlosCommitNotation/blob/main/Extension%20Intentions.md)
docs for the full notation.

## Setup

Requires [mise](https://mise.jdx.dev/); it installs Python and uv for you.

```sh
./build_and_test        # installs Python/uv via mise, syncs deps, runs tests
```

## Running the server

```sh
mise run run
```

This starts the server on stdio, ready to be connected to by an MCP client
(e.g. registered as a tool provider in an AI coding assistant).

## Development

Source lives in `src/racn_mcp/`:

- `notation.py` — RACN message formatting and validation.
- `git_commit.py` — runs the actual `git commit`.
- `server.py` — the MCP server and tool definitions.

Tests live in `tests/` and run via `./build_and_test` or `uv run pytest`.

This repo dogfoods its own notation: check `git log` for commit messages in
RACN format, and see `.claude/skills/racn-classify/SKILL.md` for the
risk/intention classification process used when committing here.
