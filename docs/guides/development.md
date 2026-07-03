---
title: Development guide
status: current
summary: How to set up, run, and contribute to Ma'at locally.
related_code:
  - .goreleaser.yaml
  - .github/workflows/release.yml
---

# Development guide

## Prerequisites

- **Go 1.24+** — to build and test Ma'at. There are no other build- or
  run-time dependencies (see [ADR 0005](../decisions/0005-go-rewrite.md)).
- Nothing else. The YAML subset parser is hand-written and vendored in the
  package, so there are no third-party modules to fetch.

## Setup

```bash
git clone <this-repo>
cd maat
go run . --help      # runs straight from the clone
```

To produce a standalone binary you can drop on your `PATH`:

```bash
go build -o maat .
./maat --help
```

## Everyday workflow

The CLI entry point is `main.go` at the repository root; the engine is the
`internal/maat/` package. The layout and responsibilities are described in the
[architecture overview](../architecture/overview.md); read it before making
structural changes.

A normal change loop:

```bash
# 1. make your code change under internal/maat/ (or main.go)
# 2. update the matching doc(s) — see AGENTS.md "update protocol"
go run . sync      # regenerate derived files if docs changed
go run . check     # validate docs (the CI gate)
go test ./...                  # run the tests
```

Both `check` and the tests must be green before you open a pull request.

## Releasing

Releases are cut by pushing a semantic-version tag. The
[`release` workflow](../../.github/workflows/release.yml) then runs
[GoReleaser](https://goreleaser.com) (config:
[`.goreleaser.yaml`](../../.goreleaser.yaml)), which cross-compiles the
binaries for linux/darwin/windows on amd64/arm64, builds the archives and
`checksums.txt`, and publishes a GitHub Release.

```bash
# 1. ensure main is green (check + tests) and the tag points at it
git tag -a v0.1.0 -m "v0.1.0"
git push origin v0.1.0        # triggers the release workflow
```

The tag is the single source of truth for the version: GoReleaser injects it
via `-ldflags` into `internal/maat`'s `version` variable, so a `v0.1.0` tag
makes the released binary report `maat 0.1.0`. A plain source build with no tag
reports the VCS pseudo-version instead (see `Version()` in `util.go`). Tags
must be `vMAJOR.MINOR.PATCH`; pre-release tags (`v0.2.0-rc1`) are published as
GitHub pre-releases automatically.

Once a tag is pushed, `go install github.com/UemitCebi/maat@latest` resolves it
through the Go module proxy.

## Coding conventions

- Standard library only — no third-party runtime dependencies.
- Keep generators pure (no I/O); all disk writes live in `sync.go`.
- Match the existing module boundaries; see
  [conventions](../meta/conventions.md).
