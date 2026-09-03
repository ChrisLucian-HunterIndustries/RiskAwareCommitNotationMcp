---
name: racn-classify
description: Classify staged changes into the correct Arlo's Risk-Aware Commit Notation (RACN) risk level and intention (including Extension Intentions) before calling the commit tool in this repo. Use whenever asked to commit using RACN.
---

# Classifying commits under Arlo's Risk-Aware Commit Notation

Before choosing `risk` and `intention` for the `commit` MCP tool, evaluate the
actual staged diff — don't default to the core four intentions (`F/B/R/D`) out
of habit. Check whether an **Extension Intention** fits better first.

This document reasons in terms of the single-character RACN symbols (`.`,
`F`, `t`, etc.), since that's the vocabulary of the underlying notation and
of this repo's own `git log`. The `commit` tool itself, however, takes the
named form of each symbol (call `notation_reference` for the authoritative
list) — e.g. pass `risk="proven_safe"` for `.`, `intention="test_only"` for
`t`, or `intention="feature_user_visible"` for the uppercase/user-visible
form of `F`. Do the classification below in symbols, then translate the
final answer to its name when calling `commit`.

## Intention: check Extension Intentions before Core Intentions

Core intentions (`F/f B/b R/r D/d`) describe changes to the product itself.
Many real commits are not about the product — check these Extension
Intentions first:

| Code | Name | Use for |
|------|------|---------|
| `e`/`E` | Environment | Non-code changes to dev setup/tooling that don't affect program behavior (`.gitignore`, `.gitattributes`, CI config, linting config, build scripts) — but not prose docs; see the note below on `e` vs `D` |
| `t`/`T` | Test-only | Changes to automated tests without altering product functionality |
| `m`/`M` | Merge | Merging branches |
| `a`/`A` | Auto | Auto-formatting or code generation |
| `c` | Comment | Comment-only changes (not doc-generation-visible) |
| `C` | Content | User-visible content changes (e.g. website copy) |
| `p`/`P` | Process | Team process/working-agreement changes |
| `s`/`S` | Spec | Spec or design document changes |
| `n`/`N` | NOP | Empty commit |

Only fall back to core intentions (`F` feature, `B` bugfix, `R` refactoring,
`D` documentation) when the change is actually about product code/behavior
and none of the extension intentions fit.

Full reference: https://github.com/RefactoringCombos/ArlosCommitNotation/blob/main/Extension%20Intentions.md

### `e` (Environment) vs core `F` — the customer-facing test

A file living in "tooling" territory (build config, package manifest) is not
automatically `e`. Ask: does this content ship as part of what a customer
installs/depends on, or is it purely internal to this team's dev workflow?

- Customer-facing → core intention (`F` for a new/changed capability, etc.),
  even if it lives in a build-config file. Example: in `pyproject.toml`, the
  `[project]` table's `name`, `version`, `description`, `requires-python`, and
  `dependencies` are exactly what an installer/consumer sees and depends on —
  that's `F`.
- Internal-only → `e`. Example: in the same `pyproject.toml`, `[dependency-groups]
  dev`, `[build-system]`, and `[tool.hatch...]` config only affect this repo's
  own build/test process — that's `e`. Likewise `mise.toml`, lockfiles
  (`uv.lock`), CI/linting config.

If a single file mixes both (as `pyproject.toml` typically does), **split the
commit**: stage/commit the customer-facing portion as `F` first, then
stage/commit the rest as `e`. Don't lump them together just because they're
in the same file.

The same test applies elsewhere, but note that `e` is for *tooling/config*,
not prose: any Markdown/plain-text doc — `README.md`, `CONTRIBUTING.md`,
`CLAUDE.md`/`AGENTS.md` instructions — is documentation (`D`/`d`) regardless
of whether its audience is package consumers or this team's own contributors
or coding agents. Reserve `e` for actual dev tooling/config (`.gitignore`,
CI workflow files, lint/build config, `mise.toml`, lockfiles).

## Risk level

Ask: what did the author do to verify this commit, and who is affected if it's wrong?

- `.` (Proven Safe) — no plausible way this breaks anything (e.g. adding a
  `.gitignore` line, dev-only tooling reviewed by eye) or a provable/tool-driven
  refactor.
- `^` (Validated) — verified via tests or an equivalent review appropriate to
  the change (e.g. ran the build/test script and confirmed it works).
- `!` (Risky) — only the intended change itself was verified; side effects
  weren't.
- `@` (Probably Broken) — no verification was possible or done.

Environment/tooling changes that are purely declarative (ignore files,
attribute files, instruction docs with no executable effect) are typically
`.`. If the change includes something executable (a script), and you actually
ran it and it worked, treat it as `.` too if the risk of it breaking anything
for the product is nil — reserve `^` for cases with real behavioral risk that
testing addressed.

Risk is scoped to production/the shipped product, not to whether the change
itself might misbehave in its own domain. A CI workflow config change (e.g.
editing the runner matrix in a GitHub Actions YAML file) cannot break
production even if it's wrong — worst case CI fails or misconfigures, which
is caught immediately and affects no one outside the team. That's `.`, even
when unverified (can't be run locally, untested runner labels, etc.). Don't
downgrade to `!` just because the change itself wasn't validated — ask
whether *production* is at risk, not whether the CI/tooling change is.

### `^` vs `!` for Feature/Bugfix — did automated tests cover it?

For core `F`/`B` changes, the deciding question is simple: **does this commit
include automated tests that exercise the change?**

- Staged code has new/changed unit tests covering it → `^` (Validated).
- Staged code has no test coverage for it → `!` (Risky) — even if you manually
  verified it works, or it's "just declarative config"; without an automated
  test, a later regression won't be caught.

Don't let LoC size be the deciding factor by itself — a small, untested change
is still `!`, and a larger change with real test coverage is still `^`. (The
notation's own `<=8 LoC` clause is one *additional* requirement for the even-
higher `.` tier, not a cap that forces `^` down to `!` when tests exist.)

## Before committing

1. Run `git diff --cached` (or review the staged file list) — don't guess
   from memory of what you staged earlier.
2. Classify each distinct concern separately if the staged diff mixes
   unrelated intentions; RACN assumes one intention per commit.
3. Prefer several small, focused commits over one large one, even within
   what looks like a single intention. If a change has independently
   separable pieces — e.g. two unrelated parameters of the same function,
   or a source change plus an unrelated cleanup it happened to touch — stage
   and commit each piece on its own rather than combining them because
   they landed in the same edit session. A good split still leaves every
   commit's tests passing on their own. When in doubt, split it. But don't
   split a change that only makes sense as a unit — e.g. moving content out
   of one file and into another (a README section relocated to a new
   CONTRIBUTING.md) is one commit, not two; splitting it would leave an
   intermediate commit that either duplicates or deletes the content with
   nowhere else for it to live.
4. State your classification and reasoning briefly before calling `commit`,
   so it's easy to correct.
