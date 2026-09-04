# Contributing

This file covers working on the project itself. Anything a user of the
server needs (what it does, how to run it) belongs in the [README](README.md)
instead.

When deciding where new content goes, the dividing line is audience, not how
the content looks: ask whether a *user* of the server needs it (README) vs.
only a *contributor working on the project itself* (here) — not whether it
looks like a shell command or dev-tooling detail. "How to run the server" is
user-facing even though it's a `mise run` command, and belongs in the README.

## Setup

Requires [mise](https://mise.jdx.dev/); it installs Python and uv for you.

```sh
./build_and_test        # installs Python/uv via mise, syncs deps, runs tests
```

See the [README](README.md) for running the server.

## Development

Source lives in `src/racn_mcp/`:

- `notation.py` — RACN message formatting and validation.
- `git_commit.py` — runs the actual `git commit`.
- `server.py` — the MCP server and tool definitions.

Tests live in `tests/` and run via `./build_and_test` or `uv run pytest`.

This repo dogfoods its own notation: check `git log` for commit messages in
RACN format, and see `.claude/skills/racn-classify/SKILL.md` for the
risk/intention classification process used when committing here.

### Regenerating embedded docs

`mise run docs` runs the MarkdownSnippets dotnet tool (config in
`mdsnippets.json`, tool manifest in `.config/dotnet-tools.json`) to embed
`docs/running-the-server.sh` into README.md as a fenced code block. It uses
two markers that are not interchangeable:

- `<!--‌ snippet: <name-or-filename> -->` — embeds a fenced code block.
  Referencing a whole file by filename (e.g. `snippet: running-the-server.sh`)
  pulls in the entire file, auto-wrapped in a fence with language detected
  from the extension, plus an anchor and a "snippet source" backlink. No
  begin/end markers are needed inside the source file for this whole-file
  form.
- `<!--‌ include: <key> -->` — splices raw markdown/prose into a document
  (e.g. a doc index). It requires the source file to be named
  `<key>.include.md`, does **not** auto-wrap content in a fence, and is not a
  substitute for `snippet:` when embedding a code file.

There is no `import:` marker — use `snippet:` for embedding code/scripts.

## Committing

Always use the `racn` MCP server's `commit` tool to commit changes in this
repository. Never run `git commit` from the command line — it is blocked.

Before committing, use the `racn` MCP's `notation_reference` tool (or the
`racn-classify` skill) to classify each change's risk level and intention.
Prefer small, focused microcommits over one large commit.
