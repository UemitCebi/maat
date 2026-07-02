"""The ``init`` command: scaffold CodeDoc into a repository.

Writes the docs tree, AGENTS.md, templates, config, and CI workflow, filling
placeholders from the project name and a short summary. Existing files are
never overwritten unless ``--force`` is passed, so re-running ``init`` is safe.
After stamping files it runs ``sync`` to generate llms.txt and adapters.
"""

from __future__ import annotations

import datetime
import os
from typing import Dict, List, Tuple

from . import scaffold, sync
from .config import load

# (relative path, scaffold attribute) for files that need placeholder filling.
_FILES: List[Tuple[str, str]] = [
    ("AGENTS.md", "AGENTS_MD"),
    ("docs/index.md", "INDEX_MD"),
    ("docs/architecture/overview.md", "ARCH_OVERVIEW"),
    ("docs/decisions/README.md", "DECISIONS_README"),
    ("docs/decisions/_template.md", "ADR_TEMPLATE"),
    ("docs/decisions/0001-record-architecture-decisions.md", "ADR_0001"),
    ("docs/guides/development.md", "GUIDE_DEVELOPMENT"),
    ("docs/guides/testing.md", "GUIDE_TESTING"),
    ("docs/guides/deployment.md", "GUIDE_DEPLOYMENT"),
    ("docs/guides/troubleshooting.md", "GUIDE_TROUBLESHOOTING"),
    ("docs/reference/configuration.md", "REFERENCE_CONFIG"),
    ("docs/reference/environment.md", "REFERENCE_ENV"),
    ("docs/meta/conventions.md", "META_CONVENTIONS"),
    ("docs/meta/glossary.md", "META_GLOSSARY"),
    ("docs/meta/maintenance.md", "META_MAINTENANCE"),
    ("templates/adr.md", "ADR_TEMPLATE"),
    ("templates/module.md", "MODULE_TEMPLATE"),
    (".codedoc.yml", "CONFIG_YML"),
    (".github/workflows/codedoc.yml", "WORKFLOW_YML"),
]


def _fill(text: str, subs: Dict[str, str]) -> str:
    for key, value in subs.items():
        text = text.replace("{{%s}}" % key, value)
    return text


def run(root: str, project: str, summary: str, force: bool) -> Dict[str, List[str]]:
    """Scaffold the framework. Returns dict with 'created' and 'skipped' lists."""
    summary = summary.strip() or "TODO: one-paragraph description of this project."
    subs = {
        "PROJECT": project,
        "SUMMARY": summary,
        "SUMMARY_INLINE": summary.replace("\n", " ")[:200],
        "DATE": datetime.date.today().isoformat(),
        "NAME": "example",
        "PATH": "src/example",
    }

    created: List[str] = []
    skipped: List[str] = []
    for rel, attr in _FILES:
        path = os.path.join(root, rel)
        if os.path.exists(path) and not force:
            skipped.append(rel)
            continue
        content = _fill(getattr(scaffold, attr), subs)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content if content.endswith("\n") else content + "\n")
        created.append(rel)

    # Generate derived artifacts (llms.txt, adapters, index nav).
    cfg = load(root)
    generated = sync.run(root, cfg)
    return {"created": created, "skipped": skipped, "generated": generated}
