---
title: 0010 Hand-copy templates live under .maat/, not the repo root
status: current
summary: init no longer scaffolds a root-level templates/ folder; the redundant ADR copy is dropped in favor of the existing docs/decisions/_template.md, and the module doc template moves to .maat/templates/_module.md, matching the leading-underscore naming already used for the ADR template.
---

# 0010. Hand-copy templates live under `.maat/`, not the repo root

- **Status:** accepted
- **Date:** 2026-07-22
- **Relates to:** [0007 Agent skills as managed artifacts](0007-agent-skills-as-managed-artifacts.md)

## Context

`init` scaffolded a root-level `templates/` folder holding two files a
developer copies by hand when writing new docs: `adr.md` and `module.md`.
This had two problems.

First, `templates/adr.md` was a byte-for-byte duplicate. `init` already
stamps `docs/decisions/_template.md` from the same source template, and that
copy — not the one in `templates/` — is the one actually referenced by the
documentation update protocol (`AGENTS.md`) and `docs/decisions/README.md`
("Copy `_template.md`..."). The root-level copy was dead weight that could
silently drift from the one developers are told to use.

Second, a two-file folder at the repo root, existing only for occasional
copy-paste, is exactly the kind of tool-owned artifact `.maat/` already
exists for. ADR 0007 established `.maat/` as where Ma'at puts generated,
tool-managed content (`.maat/skills/`) so it doesn't compete with a
project's own root-level files. `templates/` never fit that pattern.

Naming was also inconsistent between the two files: `docs/decisions/_template.md`
carries the leading-underscore convention `model-generate.md` documents
("files whose name begins with `_` ... are treated as templates/partials"),
but neither `templates/adr.md` nor `templates/module.md` did.

## Decision

**Drop the redundant ADR copy; move the module template into `.maat/`; name
both hand-copy templates with a leading underscore.**

- `init` no longer writes `templates/adr.md`. Developers copy
  `docs/decisions/_template.md` directly, as the protocol already instructs.
- `init` writes the module doc template to `.maat/templates/_module.md`
  instead of `templates/module.md`. There is no `docs/architecture/`
  equivalent to redirect to, so this template still needs a home.
- Both surviving hand-copy templates now share the `_` prefix:
  `docs/decisions/_template.md` and `.maat/templates/_module.md`.
- `init` no longer creates a root-level `templates/` folder at all.

Existing repos that already have a `templates/` folder from a prior `init`
are unaffected — `init` only ever adds files, it does not delete them.

## Consequences

- **One ADR template, not two.** There is a single file to keep current;
  nothing can drift out of sync with itself.
- **The repo root stays free of a tool-owned folder.** `.maat/` is now the
  one place to look for every hand-copy and generated Ma'at artifact.
- **Template naming is uniform.** A leading underscore consistently signals
  "copy me, don't index me" across both templates.
- **Adopters of an older Ma'at release keep their existing `templates/`
  folder** until they delete it themselves; `init` will not create a new one
  on re-run, but won't remove the old one either.

## Alternatives considered

- **Keep `templates/` at the root, just deduplicate the ADR copy.** Rejected:
  fixes the duplication but not the root-directory clutter the folder exists
  for a single remaining file.
- **Move both templates under `docs/`** (e.g. `docs/architecture/_template.md`
  next to `docs/decisions/_template.md`). Rejected: the module template isn't
  documentation content itself — it is scaffolding for creating documentation
  content — so grouping it with the other tool-managed artifacts in `.maat/`
  keeps the distinction clean and gives it a home consistent with
  `.maat/skills/`.
- **Rename `docs/decisions/_template.md` to drop its underscore instead of
  adding one to the module template.** Rejected: the underscore there isn't
  cosmetic — `model-generate.md`'s doc-scanning logic uses the leading
  underscore to skip templates/partials from indexes and validation while
  keeping them valid on-disk link targets. Removing it would require a
  different exclusion mechanism for no benefit.
