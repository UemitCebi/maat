# CodeDoc

<!--
This is the single source of truth for AI coding agents working in this
repository. It follows the AGENTS.md open standard (https://agents.md) and is
read natively by Codex, Cursor, Gemini CLI, Jules, Factory, Aider, goose,
opencode, Zed, GitHub Copilot's coding agent, Windsurf, Devin, Hermes, and
others. Agents that use a different filename are pointed here by generated
adapter files (CLAUDE.md, .github/copilot-instructions.md, .cursor/rules/…).

Keep this file concise and stable. Detailed, changing knowledge belongs in
docs/ — this file tells agents how to FIND and MAINTAIN those docs.
-->

## Project overview

CodeDoc is a **documentation-as-code framework** that keeps three things in
lockstep: a repository's `docs/` tree, its cross-agent instruction files, and
its source code. It is designed so that documentation can be maintained
interchangeably by AI coding agents, human developers, and CI — and so that
**any** agent harness (Claude Code, Copilot, Codex, Cursor, Windsurf, Hermes,
opencode, and others) discovers and updates the same docs.

CodeDoc ships a small, **zero-dependency Python CLI** (`codedoc`) with three
verbs — `init`, `sync`, `check` — and a documented convention for how the
`docs/` tree is structured and kept current.

This repository **dogfoods itself**: the docs you are reading were scaffolded
by `codedoc init` and are validated by `codedoc check` in CI.

## Where the documentation lives

All durable knowledge lives in [`docs/`](docs/). It is documentation-as-code:
versioned with the source, reviewed in pull requests, and treated as a
first-class part of every change.

- **Start here:** [`docs/llms.txt`](docs/llms.txt) — a machine-readable index
  of every document. Read it first to locate what a task needs.
- **Human entry point:** [`docs/index.md`](docs/index.md).
- Organized into:
  - [`docs/architecture/`](docs/architecture/) — how the system is built.
  - [`docs/decisions/`](docs/decisions/) — Architecture Decision Records; the
    *why*, append-only.
  - [`docs/guides/`](docs/guides/) — how to develop, test, deploy, troubleshoot.
  - [`docs/reference/`](docs/reference/) — factual surface: CLI, config,
    front-matter schema.
  - [`docs/meta/`](docs/meta/) — conventions and glossary for the docs.

## Before you change code

1. Read [`docs/llms.txt`](docs/llms.txt) and open the documents relevant to
   your task.
2. Check [`docs/decisions/`](docs/decisions/) for any ADR that constrains the
   area you are about to touch. Do not silently contradict an accepted
   decision — if one should change, write a new ADR that supersedes it.

## Documentation update protocol

**A change is not complete until its documentation is updated in the same
change.** Treat docs edits as part of the diff, never a follow-up.

When you modify code, update docs as follows:

| If you… | Then update… |
|---|---|
| Change how a module works or how modules relate | the module's page in `docs/architecture/` |
| Make a non-obvious, hard-to-reverse choice | add a new ADR in `docs/decisions/` (copy `_template.md`) |
| Change build/test/deploy/run steps | the relevant `docs/guides/` page |
| Add/rename/remove a CLI flag, config key, or front-matter field | `docs/reference/` |
| Add or move a source file a doc's `related_code` points at | that doc's `related_code` front-matter |

Then regenerate derived indexes and adapter files, and validate:

```bash
python3 -m codedoc sync      # regenerate llms.txt, docs/index.md nav, adapters
python3 -m codedoc check     # fails on stale/broken/missing/drifted docs
```

### Front-matter every doc carries

Each Markdown file in `docs/` begins with a front-matter block. The
`related_code` list is what lets tooling detect when code drifts from docs:

```markdown
---
title: Human-readable title
status: current            # current | draft | deprecated
summary: One-line description used in indexes.
related_code:              # source paths this doc describes (optional)
  - codedoc/check.py
---
```

Full schema: [`docs/reference/frontmatter.md`](docs/reference/frontmatter.md).

## Setup, build, and test commands

CodeDoc has **no runtime dependencies** — it is stdlib-only Python 3.8+.

```bash
# Run the CLI from a clone (no install needed):
python3 -m codedoc --help

# Validate the docs (this is what CI runs):
python3 -m codedoc check

# Regenerate derived files after editing docs:
python3 -m codedoc sync

# Run the test suite (needs pytest; the code itself needs nothing):
python3 -m pytest -q
```

Before declaring any change done: run `python3 -m codedoc check` **and**
`python3 -m pytest -q`, and make sure both are green.

## Human approval

Agents may draft documentation changes, but a human reviews them in the pull
request alongside the code. CI (`codedoc check`) enforces that docs were kept
in sync; the reviewer confirms they are *correct*.
