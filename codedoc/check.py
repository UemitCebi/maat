"""Validate the documentation set. Powers ``codedoc check`` (the CI gate).

Checks performed:

* **frontmatter**   — required keys present, ``status`` is a known value.
* **broken_links**  — every relative Markdown link inside docs resolves.
* **orphaned_code** — every ``related_code`` path exists on disk.
* **staleness**     — a ``related_code`` file modified more recently than its
                      doc suggests the doc may be out of date.
* **drift**         — generated artifacts (llms.txt, adapters, index) match
                      what ``sync`` would produce right now.

Each finding is a :class:`Finding` with a severity of ``error`` or ``warn``.
``check`` exits non-zero if any error-severity finding is present.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from .model import Document, DocsModel


class Finding:
    def __init__(self, severity: str, code: str, where: str, message: str) -> None:
        self.severity = severity  # "error" | "warn"
        self.code = code
        self.where = where
        self.message = message

    def __str__(self) -> str:
        icon = "✖" if self.severity == "error" else "⚠"
        return "%s [%s] %s: %s" % (icon, self.code, self.where, self.message)


def _is_external(link: str) -> bool:
    return (
        "://" in link
        or link.startswith("#")
        or link.startswith("mailto:")
        or link.startswith("//")
    )


def _ignored(path: str, prefixes: List[str]) -> bool:
    return any(path == p or path.startswith(p.rstrip("/") + "/") for p in prefixes)


def check_frontmatter(model: DocsModel, cfg: Dict[str, Any]) -> List[Finding]:
    findings: List[Finding] = []
    required = cfg.get("required_frontmatter", [])
    statuses = cfg.get("statuses", [])
    for doc in model.documents:
        for key in required:
            if not doc.meta.get(key):
                findings.append(
                    Finding("error", "frontmatter", doc.rel,
                            "missing required front-matter key %r" % key)
                )
        if statuses and doc.meta.get("status") and doc.status not in statuses:
            findings.append(
                Finding("error", "frontmatter", doc.rel,
                        "status %r not in allowed %s" % (doc.status, statuses))
            )
    return findings


def check_links(model: DocsModel, cfg: Dict[str, Any]) -> List[Finding]:
    sev = "error" if cfg["check"].get("broken_links_is_error", True) else "warn"
    findings: List[Finding] = []
    for doc in model.documents:
        doc_dir = os.path.dirname(doc.path)
        for link in doc.links():
            target = link.split("#", 1)[0].strip()
            if not target or _is_external(target):
                continue
            resolved = os.path.normpath(os.path.join(doc_dir, target))
            if not os.path.exists(resolved):
                findings.append(
                    Finding(sev, "broken_link", doc.rel,
                            "link target does not exist: %s" % link)
                )
    return findings


def check_related_code(model: DocsModel, cfg: Dict[str, Any]) -> List[Finding]:
    orphan_sev = "error" if cfg["check"].get("orphaned_code_is_error", True) else "warn"
    stale_mode = cfg["check"].get("staleness", "warn")
    ignore = cfg["check"].get("ignore_code_paths", [])
    findings: List[Finding] = []
    for doc in model.documents:
        for code_rel in doc.related_code:
            if _ignored(code_rel, ignore):
                continue
            code_path = os.path.join(model.root, code_rel)
            if not os.path.exists(code_path):
                findings.append(
                    Finding(orphan_sev, "orphaned_code", doc.rel,
                            "related_code path not found: %s" % code_rel)
                )
                continue
            if stale_mode != "off":
                if _is_stale(code_path, doc.path):
                    findings.append(
                        Finding(stale_mode, "staleness", doc.rel,
                                "code %s is newer than its doc — review and "
                                "refresh, then bump the doc's mtime (re-save) "
                                "or update it" % code_rel)
                    )
    return findings


def _is_stale(code_path: str, doc_path: str) -> bool:
    try:
        return os.path.getmtime(code_path) > os.path.getmtime(doc_path) + 1.0
    except OSError:
        return False


def check_drift(model: DocsModel, cfg: Dict[str, Any], root: str) -> List[Finding]:
    """Compare on-disk generated artifacts against freshly generated content."""
    from . import sync as sync_mod

    sev = "error" if cfg["check"].get("drift_is_error", True) else "warn"
    findings: List[Finding] = []
    for rel, expected in sync_mod.expected_artifacts(model, cfg, root).items():
        path = os.path.join(root, rel)
        actual = ""
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                actual = handle.read()
        if _normalize(actual) != _normalize(expected):
            reason = "missing — run `codedoc sync`" if not actual else \
                "out of date — run `codedoc sync`"
            findings.append(Finding(sev, "drift", rel, reason))
    return findings


def _normalize(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()


def run_all(model: DocsModel, cfg: Dict[str, Any], root: str) -> List[Finding]:
    findings: List[Finding] = []
    findings += check_frontmatter(model, cfg)
    findings += check_links(model, cfg)
    findings += check_related_code(model, cfg)
    findings += check_drift(model, cfg, root)
    # Stable ordering: errors first, then by location.
    findings.sort(key=lambda f: (0 if f.severity == "error" else 1, f.where, f.code))
    return findings
