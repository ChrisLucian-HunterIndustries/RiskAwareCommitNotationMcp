# Contributing

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

## Committing

Always use the `racn` MCP server's `commit` tool to commit changes in this
repository. Never run `git commit` from the command line — it is blocked.

Before committing, use the `racn` MCP's `notation_reference` tool (or the
`racn-classify` skill) to classify each change's risk level and intention.
Prefer small, focused microcommits over one large commit.
