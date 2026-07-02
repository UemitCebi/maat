---
title: Testing guide
status: current
summary: How to run and write CodeDoc's tests, and what CI enforces.
---

# Testing guide

## Running the tests

```bash
python3 -m pytest -q            # whole suite
python3 -m pytest tests/test_check.py -q            # one file
python3 -m pytest tests/test_check.py::test_staleness_flags_newer_code   # one test
```

The tests exercise the CLI end to end against temporary directories: they run
`init`, `sync`, and `check`, and assert on findings and exit codes.

## What CI enforces

The [`CodeDoc` workflow](../../.github/workflows/codedoc.yml) runs on every pull
request and push to the main branch. It runs:

```bash
python3 -m codedoc check --format github
```

A merge is blocked if `check` reports any error-severity finding — stale docs,
broken internal links, missing `related_code` targets, or drifted generated
files. Fix them by updating the relevant doc and running `codedoc sync`.

## Writing tests

- Tests live under `tests/` and use `pytest` with `tmp_path` for isolation.
- Prefer black-box tests that invoke `codedoc.cli.main([...])` and assert on
  the return code, over testing internal functions — this keeps the CLI
  contract (documented in the [CLI reference](../reference/cli.md)) covered.
- When you add a validation rule, add a test that proves it both *fires* on a
  bad fixture and *stays quiet* on a good one.
