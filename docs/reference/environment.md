---
title: Environment variables
status: current
summary: Environment variables Ma'at reads.
---

# Environment variables

Ma'at's **behavior** — what it validates, what exit code it returns, what
content it writes — is determined entirely by command-line arguments and the
`.maat.yml` file at the repository root (see the
[configuration reference](configuration.md)), never by ambient environment
state. If a future feature needs configuration, it belongs in `.maat.yml`,
not the environment.

Two variables affect **presentation only** — never behavior:

| Variable | Effect |
|----------|--------|
| `NO_COLOR` | Any non-empty value disables ANSI styling, even in a real terminal. |
| `CLICOLOR_FORCE` | Any value other than `0` forces ANSI styling on, even when stdout isn't a terminal. |

Neither can change a `Finding`, an exit code, or a byte of generated file
content — only whether the human-facing text printed alongside them carries
color. `--format github` output never carries color regardless of either
variable. This preserves the original goal (CI and every agent harness get
identical, reproducible *results* from the repository contents alone) while
letting a human at a real terminal get styled output. See
[ADR 0011](../decisions/0011-build-time-go-dependencies.md).
