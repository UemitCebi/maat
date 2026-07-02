---
title: Adopting CodeDoc in a repository
status: current
summary: How to add CodeDoc to an existing project and wire it into CI.
---

# Adopting CodeDoc in a repository

CodeDoc is not a service you deploy; it is a tool and a convention you adopt
into a repository. This guide covers rolling it out.

## 1. Get the tool

CodeDoc is a single static binary with no runtime dependencies (see
[ADR 0005](../decisions/0005-go-rewrite.md)). Obtain it either way:

```bash
# Build from source (requires Go 1.24+):
go build -o codedoc ./cmd/codedoc
# …then move ./codedoc onto your PATH.

# Or run without installing, from a clone of this repo:
go run ./cmd/codedoc <command>
```

A prebuilt binary can be committed to the target repo or fetched in CI; because
it is statically linked, no interpreter or package manager is required on the
machine that runs it.

## 2. Scaffold the docs

```bash
codedoc init . --name "My Project" --summary "What it does."
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
builds the binary and runs `codedoc check` on every pull request. For non-GitHub
CI, run the same command:

```bash
codedoc check --format text
```

Make the job **required** so documentation drift blocks a merge, mirroring how
a failing test does.

## 5. Establish the habit

From here, the [update protocol](../../AGENTS.md) does the work: every change
that touches code updates its docs in the same PR, `codedoc sync` regenerates
derived files, and `codedoc check` keeps everyone honest.
