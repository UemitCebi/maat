---
title: Development guide
status: current
summary: How to set up, run, and contribute to CodeDoc locally.
---

# Development guide

## Prerequisites

- **Python 3.8+** — that is the only requirement to *run* CodeDoc; it uses the
  standard library exclusively (see
  [ADR 0002](../decisions/0002-zero-dependencies.md)).
- **pytest** — only to run the test suite.

## Setup

```bash
git clone <this-repo>
cd codedoc
python3 -m codedoc --help      # runs straight from the clone, no install
```

There is nothing to build and nothing to install for normal use. To run the
tests, install pytest into a virtual environment:

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install pytest
```

## Everyday workflow

The package lives in `codedoc/`. The layout and responsibilities are described
in the [architecture overview](../architecture/overview.md); read it before
making structural changes.

A normal change loop:

```bash
# 1. make your code change under codedoc/
# 2. update the matching doc(s) — see AGENTS.md "update protocol"
python3 -m codedoc sync        # regenerate derived files if docs changed
python3 -m codedoc check       # validate docs (the CI gate)
python3 -m pytest -q           # run the tests
```

Both `check` and the tests must be green before you open a pull request.

## Coding conventions

- Standard library only in `codedoc/` — no runtime dependencies.
- Keep generators pure (no I/O); all disk writes live in `sync.py`.
- Match the existing module boundaries; see
  [conventions](../meta/conventions.md).
