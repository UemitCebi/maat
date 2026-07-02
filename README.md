# CodeDoc

**Documentation-as-code for humans _and_ AI agents.**

CodeDoc keeps three things in lockstep — a repository's `docs/` tree, its
cross-agent instruction files, and its source code — so that documentation can
be maintained interchangeably by AI coding agents, human developers, and CI.

Whatever agent harness a developer uses — GitHub Copilot, Claude Code, Codex,
Cursor, Windsurf, opencode, Hermes, Gemini CLI, and others — CodeDoc gives it a
single, discoverable source of truth and a protocol for keeping the docs
current as the code changes.

---

## Why

Two problems, one solution:

1. **Docs rot.** They live apart from the code, are updated late (if ever), and
   silently drift until they mislead. CodeDoc treats docs as part of the diff
   and gives CI a way to *fail the build* when they fall behind.
2. **Every agent looks somewhere different.** Claude reads `CLAUDE.md`, Copilot
   reads `.github/copilot-instructions.md`, Cursor reads `.cursor/rules/…`, and
   a growing set read `AGENTS.md`. Maintaining these by hand guarantees they
   diverge. CodeDoc makes **`AGENTS.md` the single source of truth** and
   *generates* every other agent's file from it, verifying they never drift.

## How it works

```
                         .codedoc.yml
                              │
                              ▼
   docs/*.md  ──scan──▶  DocsModel  ──┬── generate ──▶ llms.txt, adapters, index
  (frontmatter)                       │
                                      └── validate ──▶ pass/fail  (the CI gate)
```

- **`docs/` + `AGENTS.md`** are the source of truth — hand-written, reviewed in
  PRs, versioned with the code.
- **`docs/llms.txt`**, the per-agent adapter files, and the navigation in
  `docs/index.md` are **generated** from that source and **verified** in CI, so
  they can never silently disagree.
- Docs declare the source files they describe via `related_code` front-matter,
  which lets CI detect when code changed but its doc didn't.

## The CLI

A single static binary with zero runtime dependencies. Build it with Go 1.24+,
or run it straight from a clone:

```bash
codedoc init .     # scaffold docs/, AGENTS.md, config, CI, adapters
codedoc sync       # regenerate llms.txt + adapters + index nav
codedoc check      # validate docs; non-zero exit fails CI
```

```bash
go build -o codedoc ./cmd/codedoc   # produce the binary
go run ./cmd/codedoc <command>      # or run without installing
```

| Command | Does |
|---------|------|
| `init` | Stamps the framework into a repository (safe to re-run) |
| `sync` | Regenerates every derived file from the docs tree |
| `check` | Validates front-matter, links, `related_code`, staleness, and drift |

## What gets scaffolded

```
AGENTS.md                        ← canonical, cross-agent instructions
docs/
  index.md                       ← human entry point (managed nav block)
  llms.txt                       ← machine-readable index (generated)
  architecture/  decisions/  guides/  reference/  meta/
templates/                       ← ADR + module templates
.codedoc.yml                     ← configuration
.github/workflows/codedoc.yml    ← CI gate
CLAUDE.md  .hermes.md  GEMINI.md  .github/copilot-instructions.md
.cursor/rules/codedoc.mdc  .windsurf/rules/codedoc.md   ← generated adapters
```

## Documentation

This repository dogfoods itself — its own docs are built with CodeDoc. Start at
[`docs/llms.txt`](docs/llms.txt) (for agents) or [`docs/index.md`](docs/index.md)
(for humans). Design rationale lives in
[`docs/decisions/`](docs/decisions/).

## The update protocol

A change is not complete until its docs are updated in the same change. See
[`AGENTS.md`](AGENTS.md) for the full protocol every contributor — human or
agent — follows.

## License

MIT — see [LICENSE](LICENSE).
