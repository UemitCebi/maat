---
title: YAML & front-matter module
status: current
summary: The dependency-free parsing layer — a YAML subset and Markdown front-matter I/O.
related_code:
  - codedoc/_yaml.py
  - codedoc/frontmatter.py
---

# YAML & front-matter

## Responsibility

Provide just enough YAML to read and write document front-matter **without any
third-party dependency**. This module is the foundation the rest of CodeDoc
builds on; it is intentionally the only place that touches YAML syntax.

It is **not** a general-purpose YAML implementation. It supports the subset
that CodeDoc's front-matter and `.codedoc.yml` actually use, and nothing more.

## Key files

- `codedoc/_yaml.py` — a small recursive parser and emitter for a YAML subset:
  scalars (with `int`/`float`/`bool`/`null` coercion), quoted strings, flow
  lists (`[a, b]`), block lists (`- item`), and nested mappings by
  indentation. Exposes `parse(text) -> dict` and `dump(obj) -> str`.
- `codedoc/frontmatter.py` — splits a Markdown file into its `---`-delimited
  front-matter block and body, and rejoins them. Exposes `parse(text)` →
  `(meta: dict, body: str)` and `render(meta, body) -> str`.

## Interfaces / contracts

- `parse("")` returns `{}` — an empty or absent block is valid, never an error.
- Round-tripping is stable: `dump(parse(x))` re-parses to the same object, so
  regenerated files do not thrash in version control.
- Front-matter keys used elsewhere: `title`, `status`, `summary`,
  `related_code`. See [front-matter reference](../../reference/frontmatter.md).

## Gotchas

- The parser assumes spaces, not tabs, for indentation (as does YAML proper).
- Only the subset above is supported. If a doc needs a structure the parser
  does not handle, extend `_yaml.py` deliberately and add a test — do not reach
  for PyYAML (see [ADR 0002](../../decisions/0002-zero-dependencies.md)).
