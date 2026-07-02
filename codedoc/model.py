"""Scan the ``docs/`` tree into an in-memory model.

Both ``sync`` (which generates indexes) and ``check`` (which validates)
operate on the same :class:`DocsModel`, so the two commands can never
disagree about what the documentation set contains.
"""

from __future__ import annotations

import os
import re
from typing import Any, Dict, List, Optional

from . import frontmatter

# Ordered so generated indexes present sections in a stable, sensible order.
SECTION_ORDER = [
    "architecture",
    "decisions",
    "guides",
    "reference",
    "meta",
]

SECTION_TITLES = {
    "architecture": "Architecture — how the system is built",
    "decisions": "Decisions — why it is built that way (ADRs)",
    "guides": "Guides — how to work on it",
    "reference": "Reference — factual surface (config, env, API)",
    "meta": "Meta — conventions and glossary",
}

_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


class Document:
    """A single Markdown document within the docs tree."""

    def __init__(self, path: str, root: str, meta: Dict[str, Any], body: str) -> None:
        self.path = path
        self.rel = frontmatter.relpath(path, root)  # e.g. docs/guides/testing.md
        self.meta = meta
        self.body = body

    @property
    def section(self) -> str:
        parts = self.rel.split("/")
        return parts[1] if len(parts) > 2 else "_root"

    @property
    def title(self) -> str:
        if self.meta.get("title"):
            return str(self.meta["title"])
        match = _H1_RE.search(self.body)
        if match:
            return match.group(1)
        return os.path.splitext(os.path.basename(self.rel))[0]

    @property
    def summary(self) -> str:
        if self.meta.get("summary"):
            return str(self.meta["summary"])
        # First non-heading, non-blank line of the body.
        for line in self.body.splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith(">"):
                return stripped
        return ""

    @property
    def status(self) -> str:
        return str(self.meta.get("status", "current"))

    @property
    def related_code(self) -> List[str]:
        value = self.meta.get("related_code", [])
        if isinstance(value, str):
            return [value]
        return [str(v) for v in (value or [])]

    def links(self) -> List[str]:
        """All Markdown link targets in the body (relative + absolute)."""
        return _LINK_RE.findall(self.body)


class DocsModel:
    """The full documentation set, indexed for generation and validation."""

    def __init__(self, root: str, docs_dir: str) -> None:
        self.root = root
        self.docs_dir = docs_dir
        self.docs_path = os.path.join(root, docs_dir)
        self.documents: List[Document] = []

    @classmethod
    def scan(cls, root: str, docs_dir: str) -> "DocsModel":
        model = cls(root, docs_dir)
        if not os.path.isdir(model.docs_path):
            return model
        for dirpath, _dirnames, filenames in os.walk(model.docs_path):
            for name in sorted(filenames):
                if not name.endswith(".md"):
                    continue
                full = os.path.join(dirpath, name)
                meta, body = frontmatter.read(full)
                model.documents.append(Document(full, root, meta, body))
        model.documents.sort(key=lambda d: d.rel)
        return model

    def by_section(self) -> Dict[str, List[Document]]:
        buckets: Dict[str, List[Document]] = {}
        for doc in self.documents:
            buckets.setdefault(doc.section, []).append(doc)
        return buckets

    def find(self, rel: str) -> Optional[Document]:
        for doc in self.documents:
            if doc.rel == rel:
                return doc
        return None

    def ordered_sections(self) -> List[str]:
        present = set(self.by_section())
        ordered = [s for s in SECTION_ORDER if s in present]
        extras = sorted(present - set(SECTION_ORDER) - {"_root"})
        return ordered + extras
