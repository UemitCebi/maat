# Contributing to Ma'at

Thanks for considering a contribution. Ma'at is a small Go CLI with zero
*runtime* dependencies — see [ADR 0011](docs/decisions/0011-build-time-go-dependencies.md)
for what that does and doesn't rule out — and its own docs are built with
itself, so the same rules that apply to users of the tool apply to this
repository.

## Before you start

- Read [`AGENTS.md`](AGENTS.md) — it is the canonical source of instructions
  for anyone (human or agent) changing this repo, including the
  **documentation update protocol**: a change is not complete until its
  matching docs are updated in the same change.
- For anything beyond a small fix, check [`docs/decisions/`](docs/decisions/)
  for an ADR that constrains the area you want to touch, and open an issue to
  discuss the approach before writing code.

## Development setup

Requires Go 1.24+ and nothing else — see
[`docs/guides/development.md`](docs/guides/development.md) for the full guide.

```bash
git clone https://github.com/getmaat/maat.git
cd maat
go run . --help      # runs straight from the clone
```

## Making a change

```bash
# 1. make your code change under internal/maat/ (or main.go)
# 2. update the matching doc(s) — see AGENTS.md "update protocol"
go run . sync      # regenerate derived files if docs changed
go run . check     # validate docs (the CI gate)
go test ./...      # run the tests
```

Both `check` and `go test ./...` must be green before you open a pull
request. CI runs the same `maat check` gate on every PR.

## Coding conventions

- Build-time-only Go module dependencies are fine (they compile into the
  static binary); no runtime process, network call, or subprocess dependency
  — see [ADR 0011](docs/decisions/0011-build-time-go-dependencies.md).
- Keep generators pure (no I/O); all disk writes live in `internal/maat/sync.go`.
- Match the existing module boundaries — see
  [`docs/meta/conventions.md`](docs/meta/conventions.md) and the
  [architecture overview](docs/architecture/overview.md).

## Pull requests

- Keep PRs focused; unrelated cleanup makes review harder.
- Include the doc updates the change requires in the same PR, not a follow-up.
- Describe *why*, not just *what* — especially for anything that isn't
  obvious from the diff.

## Reporting bugs and requesting features

Use [GitHub Issues](https://github.com/getmaat/maat/issues). For
vulnerabilities, see [`SECURITY.md`](SECURITY.md) instead of filing a public
issue.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
