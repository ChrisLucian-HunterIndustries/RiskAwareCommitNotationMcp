# Committing

Always use the `racn` MCP server's `commit` tool to commit changes in this
repository. Never run `git commit` from the command line — it is blocked.

Before committing, use the `racn` MCP's `notation_reference` tool (or the
`racn-classify` skill) to classify each change's risk level and intention.
Prefer small, focused microcommits over one large commit.

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, running the server, and
development notes.
