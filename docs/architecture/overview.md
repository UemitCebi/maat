---
title: Architecture Overview
status: current
summary: How CodeDoc is built — the CLI pipeline, the docs model, and the generate/validate split.
---

# Architecture overview

CodeDoc is a small, single-package Python CLI plus a documented convention for
how a repository's `docs/` tree is structured. There is no server, no database,
and no runtime dependency — everything is stdlib Python 3.8+ so the tool can be
vendored into any repository and run anywhere.

## The three commands

Everything the user does goes through one of three verbs:

```
codedoc init    →  stamp the docs/ scaffold + AGENTS.md + config + CI into a repo
codedoc sync    →  regenerate derived files (llms.txt, adapters, index nav)
codedoc check   →  validate the docs set; exit non-zero on problems (the CI gate)
```

## Data flow

```
                         .codedoc.yml
                              │  (config.load)
                              ▼
   docs/*.md  ──scan──▶  DocsModel  ──┬── generate ──▶ llms.txt, adapters, index nav
  (frontmatter)         (model.py)    │                 (sync writes them)
                                      └── validate ──▶ Findings ──▶ exit code
                                          (check.py)              (check reports them)
```

The **single source of truth** is the `docs/` tree plus the root `AGENTS.md`.
Every other agent-facing file (`CLAUDE.md`, `.github/copilot-instructions.md`,
`.cursor/rules/codedoc.mdc`, `docs/llms.txt`, …) is *derived* by `sync` and
*verified* by `check`. This is the core invariant: **derived files never hold
original information**, so they can always be regenerated and can never
silently disagree with the source.

## Why sync and check share one function

`sync` and `check` both call `sync.expected_artifacts()`, which returns a
`{path: desired_content}` map. `sync` writes it; `check` compares the map
against what is on disk and reports "drift" for any mismatch. Because both
commands derive their notion of "correct" from the same function, the sequence
*sync then check* can never fail on drift — drift can only appear from a hand
edit to a generated file or a forgotten `sync`.

## Components

| Component | File | Responsibility |
|-----------|------|----------------|
| CLI / arg parsing | `codedoc/cli.py` | Parse args, dispatch to commands, format output |
| Docs scanner/model | `codedoc/model.py` | Walk `docs/`, parse front-matter, index documents |
| Generators | `codedoc/generate.py` | Render `llms.txt`, adapter files, index navigation |
| Sync command | `codedoc/sync.py` | Compute + write derived artifacts |
| Check command | `codedoc/check.py` | Validate front-matter, links, code refs, drift |
| Init command | `codedoc/init.py` | Stamp the scaffold into a repo |
| Scaffold content | `codedoc/scaffold.py` | Embedded starter templates for `init` |
| Config | `codedoc/config.py` | Load `.codedoc.yml`, defaults, adapter registry |
| Front-matter I/O | `codedoc/frontmatter.py` | Split/join the `---` YAML block in Markdown |
| YAML subset | `codedoc/_yaml.py` | Dependency-free YAML parser/emitter |

## Module index

- [YAML & front-matter](modules/yaml-frontmatter.md) — the dependency-free
  parsing layer everything else is built on.
- [Model & generators](modules/model-generate.md) — scanning docs and
  rendering derived artifacts.
- [Check engine](modules/check.md) — the validation rules behind the CI gate.

## Key design decisions

The *why* behind this shape is recorded as ADRs:

- [0002 Zero runtime dependencies](../decisions/0002-zero-dependencies.md)
- [0003 AGENTS.md as source of truth with generated adapters](../decisions/0003-agents-md-source-of-truth.md)
- [0004 Detect staleness via related_code timestamps](../decisions/0004-related-code-staleness.md)
