---
title: Model & generators module
status: current
summary: Scanning the docs tree into a model and rendering derived artifacts from it.
related_code:
  - codedoc/model.py
  - codedoc/generate.py
  - codedoc/sync.py
---

# Model & generators

## Responsibility

Turn the `docs/` tree into an in-memory model, and render every *derived*
artifact from that model: `llms.txt`, the per-agent adapter files, and the
managed navigation block inside `docs/index.md`.

## Key files

- `codedoc/model.py` — `DocsModel.scan(root, docs_dir)` walks the docs
  directory, parses each Markdown file's front-matter, and produces a list of
  `Document` objects (with `rel`, `meta`, `status`, `related_code`, and helpers
  to extract Markdown links). Files whose name begins with `_` (e.g.
  `decisions/_template.md`) are treated as templates/partials and skipped, so
  they never appear in indexes or validation while remaining valid link
  targets on disk.
- `codedoc/generate.py` — pure rendering functions: `llms_txt()`,
  `index_nav()`, `adapter_content()`, plus `splice()` which inserts generated
  text between `<!-- codedoc:begin -->` / `<!-- codedoc:end -->` markers
  without disturbing hand-written content around them.
- `codedoc/sync.py` — `expected_artifacts()` composes the generators into the
  full `{path: content}` map; `write_artifacts()` writes only changed files.

## Interfaces / contracts

- `expected_artifacts(model, cfg, root)` is the **single definition of
  "correct"** for every generated file. Both `sync` (writer) and `check`
  (drift detector) consume it, guaranteeing they agree.
- Generators are pure functions of the model + config; they perform no I/O.
  All disk access lives in `sync.py`, which keeps generation testable.
- `splice()` preserves everything outside the managed markers, so a human may
  freely add prose above/below the generated block in `index.md` and adapters.

## Gotchas

- `.mdc` (Cursor) adapters are generated **whole**, not spliced, because their
  YAML front-matter cannot host HTML comment markers. Editing them by hand will
  be reported as drift.
- Adapter relative paths depend on the file's directory depth (e.g.
  `.github/copilot-instructions.md` points at `../AGENTS.md`). That math lives
  in `sync._adapter_ctx()`.
