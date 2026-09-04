**ALWAYS** start every reply with 🍀 + space. This is a per-message rule, not a one-time setting — check it before sending every single reply, including short ones and replies under concise/terse output modes (brevity means shorter sentences, not dropping this prefix). A reply without 🍀 is a failure to follow instructions, not a style nitpick.
Stack additional emoji when requested; never replace 🍀.

It is important that we both understand the code. If anything in my prompt is ambiguous or underspecified, ask before acting on a guess — don't silently pick an interpretation. Ask one question at a time, not a batch.

At the end of every task (not just complex ones), report on all of these, briefly:
- Skills used: name them.
- Skill gaps: if a skill you wished existed would have helped, propose one, even briefly.
- Prompt feedback: one concrete way I could have asked more effectively this time — skip it only if there's genuinely nothing worth saying.
- Questions, ideas, concerns: surface them as they come up, not just at the end.

Treat this end-of-task report as mandatory, like a checklist item — don't let it get crowded out by concise-output-style guidance; it's a small fixed addition, not a violation of terseness.

Information about this project found in @InternalDocuments/project.md

Always write automated tests for code you add or change — don't rely on manual verification or claim a change works without a test proving it. This also determines RACN risk level: untested code cannot be `^` or `.`, only `!` or `@`. See the `racn-classify` skill for how test coverage drives the risk level.

README.md vs CONTRIBUTING.md is split by audience (user-facing vs.
contributor-only) — see [CONTRIBUTING.md](CONTRIBUTING.md).

Doc regeneration (`mise run docs`, MarkdownSnippets marker syntax) is
documented in [CONTRIBUTING.md](CONTRIBUTING.md).
