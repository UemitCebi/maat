"""The ``sync`` command: regenerate all derived artifacts.

A single function, :func:`expected_artifacts`, computes the full mapping of
``relative path -> desired content`` for every generated file. ``sync``
writes them; ``check`` compares against them. Because both commands consume
the same function, "sync then check" is guaranteed to pass — drift can only
come from hand edits to generated files or forgotten syncs.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from . import generate
from .config import adapters_for
from .model import DocsModel


def _project_meta(root: str, cfg: Dict[str, Any]) -> Dict[str, str]:
    """Best-effort project name + summary for indexes."""
    name = cfg.get("project_name") or os.path.basename(os.path.abspath(root))
    summary = cfg.get("project_summary", "")
    return {"name": str(name), "summary": str(summary)}


def expected_artifacts(model: DocsModel, cfg: Dict[str, Any], root: str) -> Dict[str, str]:
    """Return ``{relative_path: expected_content}`` for every generated file.

    Adapter files and index.md use *managed regions*: we splice the generated
    block into whatever hand-written content already exists on disk, so the
    "expected" content depends on the current file. Fully generated files
    (llms.txt) are returned whole.
    """
    artifacts: Dict[str, str] = {}
    docs_dir = cfg["docs_dir"]
    instructions = cfg["instructions_file"]
    meta = _project_meta(root, cfg)

    # 1. llms.txt — fully generated, lives at docs/llms.txt
    llms_rel = "%s/llms.txt" % docs_dir
    artifacts[llms_rel] = generate.llms_txt(model, meta["name"], meta["summary"])

    # 2. docs/index.md — managed navigation region inside a hand-written file
    index_rel = "%s/index.md" % docs_dir
    index_path = os.path.join(root, index_rel)
    existing_index = _read(index_path)
    nav = generate.index_nav(model)
    artifacts[index_rel] = generate.splice(existing_index, nav)

    # 3. Agent adapter files — managed pointer/mdc content
    for target in adapters_for(cfg):
        rel = target["path"]
        ctx = _adapter_ctx(rel, docs_dir, instructions, target["label"])
        body = generate.adapter_content(target["kind"], ctx)
        if target["kind"] == "mdc":
            # .mdc files are wholly generated (front-matter can't be spliced).
            artifacts[rel] = body
        else:
            existing = _read(os.path.join(root, rel))
            artifacts[rel] = generate.splice(existing, body)

    return artifacts


def _adapter_ctx(rel: str, docs_dir: str, instructions: str, label: str) -> Dict[str, str]:
    """Compute relative paths from an adapter file's location to the targets."""
    depth = rel.count("/")
    up = "../" * depth
    return {
        "label": label,
        "docs_dir": docs_dir,
        "instructions": instructions,
        "instructions_rel": up + instructions,
        "docs_rel": "%s%s/" % (up, docs_dir),
        "llms_rel": "%s%s/llms.txt" % (up, docs_dir),
    }


def _read(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    return ""


def write_artifacts(artifacts: Dict[str, str], root: str) -> list:
    """Write every artifact to disk, creating parent dirs. Returns changed paths."""
    changed = []
    for rel, content in artifacts.items():
        path = os.path.join(root, rel)
        if not content.endswith("\n"):
            content += "\n"
        old = _read(path)
        if old == content:
            continue
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(content)
        changed.append(rel)
    return changed


def run(root: str, cfg: Dict[str, Any]) -> list:
    model = DocsModel.scan(root, cfg["docs_dir"])
    artifacts = expected_artifacts(model, cfg, root)
    return write_artifacts(artifacts, root)
