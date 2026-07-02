"""End-to-end tests for the CodeDoc CLI.

These drive the public CLI (``codedoc.cli.main``) against temporary
repositories and assert on exit codes and findings — the same contract users
and CI depend on. No third-party fixtures; just pytest's ``tmp_path``.
"""

from __future__ import annotations

import os
import time

import pytest

from codedoc import check as check_mod
from codedoc.cli import main
from codedoc.config import load
from codedoc.model import DocsModel


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _init(root, name="TestProj", summary="A demo project."):
    return main(["init", str(root), "--name", name, "--summary", summary])


def _findings(root):
    cfg = load(str(root))
    model = DocsModel.scan(str(root), cfg["docs_dir"])
    return check_mod.run_all(model, cfg, str(root))


def _codes(findings):
    return sorted(f.code for f in findings)


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #

def test_init_creates_expected_tree(tmp_path):
    assert _init(tmp_path) == 0
    for rel in [
        "AGENTS.md",
        "docs/index.md",
        "docs/llms.txt",
        "docs/decisions/0001-record-architecture-decisions.md",
        ".codedoc.yml",
        ".github/workflows/codedoc.yml",
        "CLAUDE.md",
        ".hermes.md",
        ".github/copilot-instructions.md",
        ".cursor/rules/codedoc.mdc",
    ]:
        assert (tmp_path / rel).exists(), "missing %s" % rel


def test_init_is_idempotent_and_nondestructive(tmp_path):
    _init(tmp_path)
    agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
    # Second init must not clobber an existing file (no --force).
    _init(tmp_path)
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == agents


def test_fresh_scaffold_passes_check(tmp_path):
    _init(tmp_path)
    assert main(["check", str(tmp_path)]) == 0
    assert _findings(tmp_path) == []


# --------------------------------------------------------------------------- #
# sync
# --------------------------------------------------------------------------- #

def test_sync_is_idempotent(tmp_path):
    _init(tmp_path)
    from codedoc import sync as sync_mod

    cfg = load(str(tmp_path))
    # init already synced, so a second sync changes nothing.
    assert sync_mod.run(str(tmp_path), cfg) == []


def test_llms_txt_lists_documents(tmp_path):
    _init(tmp_path)
    llms = (tmp_path / "docs" / "llms.txt").read_text(encoding="utf-8")
    assert "Architecture Overview" in llms
    assert "docs/decisions/0001-record-architecture-decisions.md" in llms


def test_adapter_points_at_agents_md(tmp_path):
    _init(tmp_path)
    claude = (tmp_path / "CLAUDE.md").read_text(encoding="utf-8")
    assert "AGENTS.md" in claude
    assert "codedoc:begin" in claude  # managed region present


# --------------------------------------------------------------------------- #
# check: drift
# --------------------------------------------------------------------------- #

def test_drift_detected_on_hand_edit(tmp_path):
    _init(tmp_path)
    llms = tmp_path / "docs" / "llms.txt"
    llms.write_text(llms.read_text(encoding="utf-8") + "\nGARBAGE\n", encoding="utf-8")
    codes = _codes(_findings(tmp_path))
    assert "drift" in codes
    assert main(["check", str(tmp_path)]) == 1


def test_sync_fixes_drift(tmp_path):
    _init(tmp_path)
    llms = tmp_path / "docs" / "llms.txt"
    llms.write_text("clobbered", encoding="utf-8")
    assert main(["sync", str(tmp_path)]) == 0
    assert "drift" not in _codes(_findings(tmp_path))


# --------------------------------------------------------------------------- #
# check: links
# --------------------------------------------------------------------------- #

def test_broken_link_detected(tmp_path):
    _init(tmp_path)
    _write(
        str(tmp_path / "docs" / "architecture" / "modules" / "m.md"),
        "---\ntitle: M\nstatus: current\nsummary: x\n---\n"
        "# M\nSee [gone](./nope.md).\n",
    )
    assert "broken_link" in _codes(_findings(tmp_path))


def test_valid_relative_link_passes(tmp_path):
    _init(tmp_path)
    _write(
        str(tmp_path / "docs" / "architecture" / "modules" / "m.md"),
        "---\ntitle: M\nstatus: current\nsummary: x\n---\n"
        "# M\nSee [overview](../overview.md).\n",
    )
    main(["sync", str(tmp_path)])  # clear the drift the new doc introduces
    assert "broken_link" not in _codes(_findings(tmp_path))


# --------------------------------------------------------------------------- #
# check: related_code (orphan + staleness)
# --------------------------------------------------------------------------- #

def _module_doc(related):
    return (
        "---\ntitle: M\nstatus: current\nsummary: x\nrelated_code:\n  - %s\n---\n# M\n"
        % related
    )


def test_orphaned_code_detected(tmp_path):
    _init(tmp_path)
    _write(
        str(tmp_path / "docs" / "architecture" / "modules" / "m.md"),
        _module_doc("src/does/not/exist.py"),
    )
    assert "orphaned_code" in _codes(_findings(tmp_path))


def test_staleness_flags_newer_code(tmp_path):
    _init(tmp_path)
    code = tmp_path / "src" / "thing.py"
    _write(str(code), "print('hi')\n")
    doc = tmp_path / "docs" / "architecture" / "modules" / "m.md"
    _write(str(doc), _module_doc("src/thing.py"))
    main(["sync", str(tmp_path)])
    # Make the code strictly newer than the doc.
    future = time.time() + 10
    os.utime(str(code), (future, future))

    findings = _findings(tmp_path)
    stale = [f for f in findings if f.code == "staleness"]
    assert stale and stale[0].severity == "warn"
    # Default check: staleness is a warning, so exit stays 0.
    assert main(["check", str(tmp_path)]) == 0
    # Strict mode promotes it to an error.
    assert main(["check", str(tmp_path), "--strict"]) == 1


def test_ignore_code_paths_suppresses_staleness(tmp_path):
    _init(tmp_path)
    code = tmp_path / "vendor" / "lib.py"
    _write(str(code), "x = 1\n")
    doc = tmp_path / "docs" / "architecture" / "modules" / "m.md"
    _write(str(doc), _module_doc("vendor/lib.py"))
    main(["sync", str(tmp_path)])
    future = time.time() + 10
    os.utime(str(code), (future, future))

    # Add vendor/ to ignore list.
    cfg_path = tmp_path / ".codedoc.yml"
    cfg_path.write_text(
        cfg_path.read_text(encoding="utf-8").replace(
            "ignore_code_paths: []", "ignore_code_paths:\n    - vendor/"
        ),
        encoding="utf-8",
    )
    codes = _codes(_findings(tmp_path))
    assert "staleness" not in codes
    assert "orphaned_code" not in codes


# --------------------------------------------------------------------------- #
# check: frontmatter
# --------------------------------------------------------------------------- #

def test_missing_required_frontmatter_detected(tmp_path):
    _init(tmp_path)
    _write(
        str(tmp_path / "docs" / "architecture" / "modules" / "m.md"),
        "---\nsummary: no title or status\n---\n# M\n",
    )
    assert "frontmatter" in _codes(_findings(tmp_path))


def test_unknown_status_detected(tmp_path):
    _init(tmp_path)
    _write(
        str(tmp_path / "docs" / "architecture" / "modules" / "m.md"),
        "---\ntitle: M\nstatus: bogus\nsummary: x\n---\n# M\n",
    )
    assert "frontmatter" in _codes(_findings(tmp_path))


# --------------------------------------------------------------------------- #
# check: misconfiguration
# --------------------------------------------------------------------------- #

def test_check_without_docs_exits_2(tmp_path):
    assert main(["check", str(tmp_path)]) == 2


# --------------------------------------------------------------------------- #
# scan: templates/partials
# --------------------------------------------------------------------------- #

def test_underscore_files_excluded_from_model(tmp_path):
    _init(tmp_path)
    rels = {d.rel for d in DocsModel.scan(str(tmp_path), "docs").documents}
    # The ADR template ships as decisions/_template.md and must not be a doc.
    assert not any(r.endswith("_template.md") for r in rels)


def test_underscore_template_not_in_generated_index(tmp_path):
    _init(tmp_path)
    llms = (tmp_path / "docs" / "llms.txt").read_text(encoding="utf-8")
    index = (tmp_path / "docs" / "index.md").read_text(encoding="utf-8")
    assert "_template.md" not in llms
    assert "_template.md" not in index


def test_link_to_underscore_template_is_valid(tmp_path):
    _init(tmp_path)
    # decisions/README.md links to _template.md; excluding it from the model
    # must not make that link look broken (file still exists on disk).
    assert "broken_link" not in _codes(_findings(tmp_path))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
