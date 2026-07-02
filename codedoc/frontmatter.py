"""Read and write YAML front-matter blocks in Markdown documents.

A CodeDoc document begins with a fenced front-matter block::

    ---
    title: Something
    status: current
    ---

    # Body starts here

This module extracts that block into a dict (using the stdlib-only
:mod:`codedoc._yaml` parser) and can splice an updated block back in without
disturbing the body.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Tuple

from . import _yaml

FENCE = "---"


class FrontMatterError(ValueError):
    """Raised when a document's front-matter is malformed."""


def split(text: str) -> Tuple[Dict[str, Any], str]:
    """Return ``(metadata, body)`` for a Markdown document.

    If the document has no front-matter, ``metadata`` is an empty dict and
    ``body`` is the whole text. A fence that opens but never closes is an
    error rather than a silent pass, so authors notice typos early.
    """
    # Tolerate a leading BOM and blank lines before the fence.
    probe = text.lstrip("\ufeff")
    leading_ws = text[: len(text) - len(probe)]
    if not probe.startswith(FENCE + "\n") and probe.rstrip() != FENCE:
        return {}, text

    lines = probe.split("\n")
    if lines[0].strip() != FENCE:
        return {}, text

    closing = None
    for i in range(1, len(lines)):
        if lines[i].strip() == FENCE:
            closing = i
            break
    if closing is None:
        raise FrontMatterError("front-matter opened with '---' but never closed")

    raw_meta = "\n".join(lines[1:closing])
    body = "\n".join(lines[closing + 1 :])
    # Drop exactly one blank separator line after the closing fence.
    if body.startswith("\n"):
        body = body[1:]
    meta = _yaml.parse(raw_meta) if raw_meta.strip() else {}
    if not isinstance(meta, dict):
        raise FrontMatterError("front-matter must be a mapping, got %s" % type(meta).__name__)
    return meta, leading_ws.replace("\ufeff", "") + body


def join(meta: Dict[str, Any], body: str) -> str:
    """Inverse of :func:`split`. Emits a normalized front-matter block."""
    if not meta:
        return body
    block = _yaml.emit(meta)
    return "%s\n%s\n%s\n\n%s" % (FENCE, block, FENCE, body.lstrip("\n"))


def read(path: str) -> Tuple[Dict[str, Any], str]:
    """Read a file and split it into ``(metadata, body)``."""
    with open(path, "r", encoding="utf-8") as handle:
        return split(handle.read())


def update(path: str, meta: Dict[str, Any]) -> None:
    """Rewrite ``path`` with new metadata, preserving the body verbatim."""
    _, body = read(path)
    new = join(meta, body)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(new if new.endswith("\n") else new + "\n")


def relpath(path: str, root: str) -> str:
    """POSIX-style path relative to ``root`` (stable across OSes)."""
    rel = os.path.relpath(path, root)
    return rel.replace(os.sep, "/")
