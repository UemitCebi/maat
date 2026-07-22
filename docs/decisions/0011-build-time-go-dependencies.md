---
title: 0011 Build-time Go dependencies are permitted; runtime dependencies are not
status: current
summary: Go module dependencies that compile statically into the binary (no external runtime process, no network call, no subprocess) are permitted going forward. The Charm libraries (Lip Gloss, Huh, and Bubble Tea transitively via Huh) are the first exercise of this policy, used for terminal styling and an interactive `init` wizard.
---

# 0011. Build-time Go dependencies are permitted; runtime dependencies are not

- **Status:** accepted
- **Date:** 2026-07-22
- **Relates to:** [0002 Zero runtime dependencies](0002-zero-dependencies.md) (deprecated), [0005 Rewrite the CLI in Go, distribute a single static binary](0005-go-rewrite.md)

## Context

Ma'at has had zero third-party dependencies of any kind since its inception —
`go.mod` carried no `require` block at all. That was never a written rule for
the Go era specifically; it was inherited unexamined from ADR 0002's Python-era
"zero runtime dependencies" goal, and repeated as "zero-dependency Go CLI" in
`AGENTS.md`, `CONTRIBUTING.md`, and several docs without anyone asking whether
it meant *zero Go module dependencies* or *zero runtime dependencies*.

ADR 0005 already answered this, in passing, without anyone acting on it:

> a Go dependency such as a YAML library compiles *into* the binary as a
> build-time dependency with zero runtime cost.

The distinction ADR 0002 actually cared about — and the reason it existed at
all — was runtime friction: a team on a pure Go/Rust/Node stack having to
install a Python interpreter, or `pip install` a package, just to run `maat`.
A Go module dependency that compiles statically into the one binary Ma'at
already ships adds none of that friction. It was never the thing ADR 0002 was
protecting against; it just hadn't come up, because until now nobody had
proposed adding one.

The occasion for finally writing this down: adding terminal-UX libraries from
the Charm ecosystem (Lip Gloss for styled output, Huh for an interactive form —
which pulls in Bubble Tea and Bubbles transitively, since a Huh form's `.Run()`
*is* a Bubble Tea program) to `maat init`'s output and prompt experience.

## Decision

**Go module dependencies that compile statically into the binary are
permitted.** A dependency qualifies if, at run time, it:

- spawns no subprocess,
- makes no network call, and
- requires no interpreter, runtime, or system package beyond what the Go
  toolchain already statically links.

Dependencies that fail any of these remain forbidden — that is the actual
"zero runtime dependencies" goal ADR 0002 established and ADR 0005 preserved,
now stated as a positive test instead of inferred from "zero-dependency."

This ADR does **not** mean dependencies are free to add. New ones should still
be justified — vetted for maintenance activity, license, and the size they add
to the binary and to the dependency graph a contributor has to reason about —
but that is ordinary engineering judgment applied per-PR, not an architectural
gate requiring an ADR each time. This ADR is the one-time act of writing down
the criterion; it does not need to be re-litigated for each future build-time
dependency.

**First exercise of this policy:** `github.com/charmbracelet/lipgloss`,
`github.com/charmbracelet/huh` (and its transitive `bubbletea`/`bubbles`) are
added to style `init`/`sync`/`check`'s human-facing output and to prompt
interactively for `init`'s name/summary when run with no flags in a real
terminal. None of the three call out to a subprocess or the network.

A narrow related consequence: styling needs to know whether to suppress color
(`NO_COLOR`) or force it (`CLICOLOR_FORCE`), which means reading two
environment variables. `docs/reference/environment.md` previously stated
Ma'at reads *no* environment variables at all; see its Consequences entry
below for the scoped exception this ADR carves out.

## Consequences

- Ma'at can now use Go's package ecosystem for things genuinely better solved
  by a well-maintained library than hand-rolled code — the same trade already
  made once, deliberately, for `go.mod` deps in general when the project moved
  off "stdlib-only Python" to "Go, full stop" in ADR 0005.
- The binary grows (Charm's transitive graph is real, if modest) and
  cross-compiling still works unchanged — none of Charm's core packages need
  cgo; the existing `CGO_ENABLED=0` build matrix is untouched.
- `CONTRIBUTING.md`, `AGENTS.md`, `docs/meta/maintenance.md`, and
  `docs/guides/development.md` all asserted "zero-dependency"/"no third-party
  modules" in ways that were only ever true of *runtime* dependencies; they are
  updated alongside this ADR to state the actual criterion instead of the
  broader claim that happened to be true only because no one had tested it.
- `docs/reference/environment.md`'s "Ma'at reads no environment variables"
  claim gets a scoped exception: `NO_COLOR` and `CLICOLOR_FORCE` affect only
  the ANSI styling wrapped around otherwise-identical text — never validation
  results, exit codes, or file content — so CI reproducibility is unaffected.
  `.maat.yml` remains the only source of *behavioral* configuration.
- A future proposal for a dependency that fails the three-part test above
  (e.g. something that shells out, or phones home) still needs its own ADR,
  the way any hard-to-reverse architectural choice does.

## Alternatives considered

- **Keep "zero dependencies, full stop.".** Rejected: it was never a
  considered position for the Go era, only an unexamined holdover from the
  Python-era rationale that ADR 0005 had already superseded in substance —
  continuing to enforce it by inertia costs real UX (no styling, no
  interactive prompts) for a risk (runtime friction) that build-time-only Go
  deps don't actually carry.
- **Vendor a hand-rolled subset, as ADR 0002 did for YAML.** Rejected here:
  that trade made sense for a small, stable, well-specified format (YAML
  front-matter) Ma'at could scope down safely. A terminal styling/TUI library
  is a much larger surface (terminal capability detection, input handling
  across platforms) where a hand-rolled subset would be a correctness
  liability for no real benefit, unlike the YAML case.
- **A blanket "case-by-case, no policy" approach.** Rejected: Ma'at's own
  documentation-as-code discipline expects a hard-to-reverse choice like "this
  project now accepts third-party Go dependencies" to be recorded, not
  inferred from a diff.
