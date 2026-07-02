---
title: Environment variables
status: current
summary: Environment variables CodeDoc reads.
---

# Environment variables

CodeDoc reads **no environment variables**. Its behaviour is determined
entirely by command-line arguments and the `.codedoc.yml` file at the
repository root (see the [configuration reference](configuration.md)).

This is deliberate: a tool that CI and multiple agent harnesses invoke should
be reproducible from the repository contents alone, with no hidden ambient
state. If a future feature needs configuration, it belongs in `.codedoc.yml`,
not the environment.
