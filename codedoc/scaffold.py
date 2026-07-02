"""Embedded scaffold content for ``codedoc init``.

These templates are written into a target repository the first time CodeDoc
is adopted. They are deliberately generic and language-agnostic: placeholders
in ``{{DOUBLE_BRACES}}`` are filled from the project name / detected facts,
and every file is safe to commit as-is and edit later.

Only ``init`` uses these. The CodeDoc repo's *own* docs are hand-written
(richer than the scaffold) so the project dogfoods the framework.
"""

from __future__ import annotations

# --------------------------------------------------------------------------- #
# AGENTS.md — the canonical, cross-agent instruction file
# --------------------------------------------------------------------------- #

AGENTS_MD = """\
# {{PROJECT}}

<!--
This is the single source of truth for AI coding agents working in this
repository. It follows the AGENTS.md open standard (https://agents.md) and is
read natively by Codex, Cursor, Gemini CLI, Jules, Factory, Aider, goose,
opencode, Zed, GitHub Copilot's coding agent, Windsurf, Devin, Hermes, and
others. Agents that use a different filename are pointed here by generated
adapter files (CLAUDE.md, .github/copilot-instructions.md, etc.).

Keep this file concise and stable. Detailed, changing knowledge belongs in
docs/ — this file tells agents how to FIND and MAINTAIN those docs.
-->

## Project overview

{{SUMMARY}}

<!-- Replace with 2-4 sentences: what this project is, who uses it, and the
one or two things an agent most needs to know before touching the code. -->

## Where the documentation lives

All durable knowledge lives in [`docs/`](docs/). It is documentation-as-code:
versioned with the source, reviewed in pull requests, and treated as a
first-class part of every change.

- **Start here:** [`docs/llms.txt`](docs/llms.txt) — a machine-readable index
  of every document. Read it first to locate what a task needs.
- **Human entry point:** [`docs/index.md`](docs/index.md).
- Documentation is organized into:
  - `docs/architecture/` — how the system is built (the *what*).
  - `docs/decisions/` — Architecture Decision Records; the *why*, append-only.
  - `docs/guides/` — how to develop, test, deploy, troubleshoot (the *how*).
  - `docs/reference/` — factual surface: configuration, environment, API.
  - `docs/meta/` — conventions and glossary for the docs themselves.

## Before you change code

1. Read [`docs/llms.txt`](docs/llms.txt) and open the documents relevant to
   your task.
2. Check `docs/decisions/` for any ADR that constrains the area you are about
   to touch. Do not silently contradict an accepted decision — if you believe
   one should change, write a new ADR that supersedes it.

## Documentation update protocol

**A change is not complete until its documentation is updated in the same
change.** Treat docs edits as part of the diff, never a follow-up.

When you modify code, update docs as follows:

| If you… | Then update… |
|---|---|
| Change how a module works or relate to each other | the module's page in `docs/architecture/` |
| Make a non-obvious, hard-to-reverse choice | add a new ADR in `docs/decisions/` (copy `_template.md`) |
| Change build/test/deploy/run steps | the relevant `docs/guides/` page |
| Add/rename/remove config keys, env vars, or public API | `docs/reference/` |
| Add or move a source file that a doc's `related_code` points at | that doc's `related_code` front-matter |

Then regenerate derived indexes and adapter files:

```bash
python -m codedoc sync      # or: codedoc sync
```

And validate before committing:

```bash
python -m codedoc check     # fails on stale/broken/missing docs
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
  - src/module/thing.ext
---
```

## Human approval

Agents may draft documentation changes, but a human reviews them in the pull
request alongside the code. The CI check (`codedoc check`) enforces that docs
were updated; the reviewer confirms they are *correct*.

## Setup, build, and test commands

<!-- Fill these in so agents can run the project's checks. Examples: -->
<!--
- Install: `...`
- Test: `...`
- Lint: `...`
-->
"""

# --------------------------------------------------------------------------- #
# docs/index.md
# --------------------------------------------------------------------------- #

INDEX_MD = """\
---
title: {{PROJECT}} Documentation
status: current
summary: Entry point and map for the {{PROJECT}} documentation set.
---

# {{PROJECT}} documentation

Welcome. This documentation is **documentation-as-code**: it lives with the
source, is reviewed in pull requests, and is kept in sync by the `codedoc`
tool. AI agents read [`llms.txt`](llms.txt) (the machine-readable index);
humans can use the map below.

> The navigation list below is generated by `codedoc sync`. Add prose above or
> below the managed block; do not edit inside it.

## Map

<!-- codedoc:begin (generated — edit the source docs, not this block) -->
<!-- codedoc:end -->

## How this documentation works

- **Architecture** answers *what exists and how it fits together*.
- **Decisions** (ADRs) answer *why it is the way it is* — an append-only log.
- **Guides** answer *how do I do X* — build, test, deploy, troubleshoot.
- **Reference** is the factual surface — config keys, env vars, API.
- **Meta** documents the documentation's own conventions.

See [`meta/maintenance.md`](meta/maintenance.md) for how to keep it current.
"""

# --------------------------------------------------------------------------- #
# Section landing pages + starter docs
# --------------------------------------------------------------------------- #

ARCH_OVERVIEW = """\
---
title: Architecture Overview
status: current
summary: High-level shape of the system — components and how they interact.
---

# Architecture overview

<!-- Describe the big picture first: the major components, the flow of data or
control between them, and the boundaries. A diagram (even ASCII) helps. Link
to per-module pages under modules/ for detail. -->

## Components

<!-- List the major components and one line each. -->

## How a request/task flows

<!-- Trace one representative path end to end. -->

## Module index

<!-- Link to docs/architecture/modules/*.md as you add them. -->
"""

MODULE_TEMPLATE = """\
---
title: {{NAME}} module
status: current
summary: What the {{NAME}} module does and how to work on it.
related_code:
  - {{PATH}}
---

# {{NAME}}

## Responsibility

<!-- One paragraph: what this module is responsible for, and explicitly what
it is NOT responsible for. -->

## Key files

<!-- Bullet the important files and their roles. -->

## Interfaces / contracts

<!-- Inputs, outputs, invariants other code depends on. -->

## Gotchas

<!-- Non-obvious behaviour, sharp edges, things that have bitten people. -->
"""

DECISIONS_README = """\
---
title: Architecture Decision Records
status: current
summary: Index of ADRs — the append-only log of why the system is the way it is.
---

# Decisions (ADRs)

An **Architecture Decision Record** captures one significant, hard-to-reverse
choice: the context, the decision, and its consequences. ADRs are
**append-only** — you do not edit an accepted decision to change its meaning.
To change direction, add a new ADR that supersedes the old one and set the old
one's status to `deprecated`.

Copy [`_template.md`](_template.md) to `NNNN-short-title.md` (next number).

## Log

<!-- List ADRs newest first as you add them, e.g.:
- [0001 Record architecture decisions](0001-record-architecture-decisions.md)
-->
"""

ADR_TEMPLATE = """\
---
title: NNNN Short title of the decision
status: current
summary: One line — the decision in a sentence.
---

# NNNN. Short title of the decision

- **Status:** proposed <!-- proposed | accepted | deprecated | superseded by ADR-XXXX -->
- **Date:** YYYY-MM-DD

## Context

<!-- What is the situation and the forces at play? Why does a decision need to
be made now? Keep it factual. -->

## Decision

<!-- State the decision in active voice: "We will …". -->

## Consequences

<!-- What becomes easier or harder as a result? Include the negative ones —
they are the most useful to a future reader. -->

## Alternatives considered

<!-- What else was on the table and why it was not chosen. -->
"""

ADR_0001 = """\
---
title: 0001 Record architecture decisions
status: current
summary: We will use Architecture Decision Records to document significant choices.
---

# 0001. Record architecture decisions

- **Status:** accepted
- **Date:** {{DATE}}

## Context

The project needs a durable, reviewable record of significant technical
choices so that future contributors — human and AI — understand *why* the
system is shaped the way it is, not just *how* it currently works.

## Decision

We will keep Architecture Decision Records (ADRs) in `docs/decisions/`, one
Markdown file per decision, numbered sequentially. ADRs are append-only: an
accepted ADR is never rewritten to mean something different; instead a new ADR
supersedes it.

## Consequences

- Contributors can trace the reasoning behind the codebase.
- Agents can read prior decisions before proposing changes and avoid silently
  contradicting them.
- A small amount of discipline is required to add an ADR when making a
  significant choice.

## Alternatives considered

- **Commit messages / PR descriptions only** — not discoverable enough; the
  reasoning gets buried in history.
- **A wiki** — drifts from the code because it is not reviewed with the code.
"""

GUIDE_DEVELOPMENT = """\
---
title: Development guide
status: current
summary: How to set up, run, and contribute to the project locally.
---

# Development guide

## Prerequisites

<!-- Languages, runtimes, tools and versions. -->

## Setup

<!-- Exact commands to get from a fresh clone to a running dev environment. -->

## Everyday workflow

<!-- How to run the app, run tests, and the expected loop. -->

## Coding conventions

<!-- Point at docs/meta/conventions.md or state the essentials. -->
"""

GUIDE_TESTING = """\
---
title: Testing guide
status: current
summary: How to run and write tests, and what the CI expects to be green.
---

# Testing guide

## Running the tests

<!-- The command(s). Include how to run a single test. -->

## What CI enforces

<!-- Which checks gate a merge, including `codedoc check`. -->

## Writing tests

<!-- Conventions: where tests live, naming, fixtures. -->
"""

GUIDE_DEPLOYMENT = """\
---
title: Deployment guide
status: current
summary: How the project is built and released to its environments.
---

# Deployment guide

<!-- Build artifacts, environments, promotion flow, rollback. If not
applicable yet, say so and set status: draft. -->
"""

GUIDE_TROUBLESHOOTING = """\
---
title: Troubleshooting
status: current
summary: Common failures and how to resolve them.
---

# Troubleshooting

<!-- Symptom -> cause -> fix. Grow this from real incidents. -->
"""

REFERENCE_CONFIG = """\
---
title: Configuration reference
status: current
summary: Every configuration option, its default, and its effect.
---

# Configuration reference

<!-- Table of config keys. Keep exhaustive; agents rely on this being complete. -->

| Key | Default | Description |
|-----|---------|-------------|
| | | |
"""

REFERENCE_ENV = """\
---
title: Environment variables
status: current
summary: Environment variables the project reads, and what they do.
---

# Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| | | |
"""

META_CONVENTIONS = """\
---
title: Documentation conventions
status: current
summary: The rules this documentation set follows so it stays consistent.
---

# Documentation conventions

- **Language:** English, always.
- **One topic per file.** Prefer many small pages over few large ones.
- **Front-matter is required** on every page: at minimum `title` and `status`.
  Add `summary` (used in indexes) and `related_code` (enables staleness
  detection) wherever they apply.
- **Status values:** `current`, `draft`, `deprecated`.
- **Link by relative path** to other docs so links survive moves and are
  validated by `codedoc check`.
- **Generated regions** (between `<!-- codedoc:begin -->` and
  `<!-- codedoc:end -->`) and generated files (`llms.txt`, adapter files) are
  produced by `codedoc sync` — never hand-edit them.
- **Decisions are append-only.** See `docs/decisions/`.
"""

META_GLOSSARY = """\
---
title: Glossary
status: current
summary: Definitions of domain and project-specific terms.
---

# Glossary

<!-- Term — definition. Alphabetical. Keeps agents and humans speaking the
same language. -->
"""

META_MAINTENANCE = """\
---
title: Maintaining the documentation
status: current
summary: How the docs stay in sync with the code — the lifecycle and tooling.
---

# Maintaining the documentation

This documentation is kept current by three actors and one tool.

## The actors

1. **AI agents** update the relevant docs in the same change they make to the
   code, following the "Documentation update protocol" in the root
   `AGENTS.md`. A human approves the result in review.
2. **Developers** editing by hand do the same, using the templates in
   `templates/` and the conventions in `conventions.md`.
3. **CI/CD** runs `codedoc check` on every pull request and fails the build if
   documentation is stale, links are broken, or generated files drifted.

## The tool

`codedoc` is a zero-dependency Python CLI:

- `codedoc sync` — regenerate `llms.txt`, `docs/index.md` navigation, and the
  per-agent adapter files from the docs tree.
- `codedoc check` — validate front-matter, links, `related_code` paths,
  staleness, and drift. This is the CI gate.
- `codedoc init` — scaffold this structure into a repository.

## Staleness detection

When a doc declares `related_code`, `codedoc check` compares modification
times. If the code is newer than the doc, it flags the doc for review. After
refreshing the doc, re-save it (or run `codedoc sync`) so its timestamp
advances.
"""

# --------------------------------------------------------------------------- #
# .codedoc.yml
# --------------------------------------------------------------------------- #

CONFIG_YML = """\
# CodeDoc configuration. All keys are optional; defaults shown below.
project_name: {{PROJECT}}
project_summary: {{SUMMARY_INLINE}}

docs_dir: docs
instructions_file: AGENTS.md

# Per-agent adapter files to generate and keep in sync with AGENTS.md.
# Remove any your team does not use.
adapters:
  - claude
  - hermes
  - copilot
  - cursor
  - windsurf
  - gemini

required_frontmatter:
  - title
  - status

statuses:
  - current
  - draft
  - deprecated

check:
  orphaned_code_is_error: true
  broken_links_is_error: true
  drift_is_error: true
  # off | warn | error — how to treat a doc whose related_code is newer.
  staleness: warn
  ignore_code_paths: []
"""

# --------------------------------------------------------------------------- #
# GitHub Actions workflow
# --------------------------------------------------------------------------- #

WORKFLOW_YML = """\
name: CodeDoc

# Validates that documentation stayed in sync with code on every pull request.
on:
  pull_request:
  push:
    branches: [main, master]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.x"
      - name: Run codedoc check
        run: |
          # CodeDoc is dependency-free stdlib Python. If vendored, adjust path.
          python -m codedoc check --format github
"""
