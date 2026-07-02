---
title: Adopting CodeDoc in a repository
status: current
summary: How to add CodeDoc to an existing project and wire it into CI.
---

# Adopting CodeDoc in a repository

CodeDoc is not a service you deploy; it is a tool and a convention you adopt
into a repository. This guide covers rolling it out.

## 1. Vendor the tool

Because CodeDoc has no dependencies (see
[ADR 0002](../decisions/0002-zero-dependencies.md)), the simplest adoption is
to copy the `codedoc/` package into the target repository and run it with
`python3 -m codedoc`. (A future packaged release may be installable from an
index; vendoring always works.)

## 2. Scaffold the docs

```bash
python3 -m codedoc init . --name "My Project" --summary "What it does."
```

This creates `AGENTS.md`, the `docs/` tree, `templates/`, `.codedoc.yml`, the
CI workflow, and generates `llms.txt` and the agent adapter files. Existing
files are not overwritten.

## 3. Fill in the starters

Edit `AGENTS.md`'s project overview and the scaffolded docs. Delete adapters
you do not need from `.codedoc.yml` and re-run `codedoc sync`. Commit
everything, including the generated files (agents read them from a fresh
clone).

## 4. Wire up CI

The generated [`.github/workflows/codedoc.yml`](../../.github/workflows/codedoc.yml)
runs `codedoc check` on every pull request. For non-GitHub CI, run the same
command:

```bash
python3 -m codedoc check --format text
```

Make the job **required** so documentation drift blocks a merge, mirroring how
a failing test does.

## 5. Establish the habit

From here, the [update protocol](../../AGENTS.md) does the work: every change
that touches code updates its docs in the same PR, `codedoc sync` regenerates
derived files, and `codedoc check` keeps everyone honest.
