"""Command-line interface for CodeDoc.

Usage::

    codedoc init [--name NAME] [--summary TEXT] [--force] [PATH]
    codedoc sync [PATH]
    codedoc check [--format text|github] [--strict] [PATH]

All commands operate on a repository root (default: current directory). The
tool is dependency-free; ``python -m codedoc <cmd>`` works anywhere.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List, Optional

from . import __version__


def _root(path: Optional[str]) -> str:
    return os.path.abspath(path or ".")


def _cmd_init(args: argparse.Namespace) -> int:
    from . import init as init_mod

    root = _root(args.path)
    name = args.name or os.path.basename(root)
    result = init_mod.run(root, name, args.summary or "", args.force)

    for rel in result["created"]:
        print("  create  %s" % rel)
    for rel in result["skipped"]:
        print("  skip    %s (exists; use --force to overwrite)" % rel)
    for rel in result.get("generated", []):
        print("  gen     %s" % rel)
    print(
        "\nCodeDoc initialized in %s\n"
        "Next: edit AGENTS.md's project overview, then run `codedoc check`."
        % root
    )
    return 0


def _cmd_sync(args: argparse.Namespace) -> int:
    from .config import load
    from . import sync as sync_mod

    root = _root(args.path)
    cfg = load(root)
    changed = sync_mod.run(root, cfg)
    if not changed:
        print("Already in sync — no files changed.")
    else:
        for rel in changed:
            print("  update  %s" % rel)
        print("\nSynced %d file(s)." % len(changed))
    return 0


def _cmd_check(args: argparse.Namespace) -> int:
    from .config import load
    from . import check as check_mod
    from .model import DocsModel

    root = _root(args.path)
    cfg = load(root)
    if args.strict:
        cfg["check"]["staleness"] = "error"

    docs_path = os.path.join(root, cfg["docs_dir"])
    if not os.path.isdir(docs_path):
        print("No %s/ directory found. Run `codedoc init` first." % cfg["docs_dir"],
              file=sys.stderr)
        return 2

    model = DocsModel.scan(root, cfg["docs_dir"])
    findings = check_mod.run_all(model, cfg, root)

    errors = [f for f in findings if f.severity == "error"]
    warnings = [f for f in findings if f.severity == "warn"]

    if args.format == "github":
        _emit_github(findings, root)
    else:
        for finding in findings:
            print(str(finding))

    total_docs = len(model.documents)
    summary = "Checked %d document(s): %d error(s), %d warning(s)." % (
        total_docs, len(errors), len(warnings))
    print("\n" + summary)

    if errors:
        return 1
    return 0


def _emit_github(findings: List, root: str) -> None:
    """Emit GitHub Actions workflow annotations."""
    for finding in findings:
        level = "error" if finding.severity == "error" else "warning"
        path = finding.where if os.path.sep in finding.where or "/" in finding.where else ""
        loc = "file=%s," % path if path else ""
        print("::%s %stitle=codedoc %s::%s" % (level, loc, finding.code, finding.message))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codedoc",
        description="Documentation-as-code for humans and AI agents.",
    )
    parser.add_argument("--version", action="version",
                        version="codedoc %s" % __version__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="scaffold CodeDoc into a repository")
    p_init.add_argument("path", nargs="?", help="repo root (default: cwd)")
    p_init.add_argument("--name", help="project name (default: dir name)")
    p_init.add_argument("--summary", help="one-line project summary")
    p_init.add_argument("--force", action="store_true",
                        help="overwrite existing scaffold files")
    p_init.set_defaults(func=_cmd_init)

    p_sync = sub.add_parser("sync", help="regenerate llms.txt, adapters, index")
    p_sync.add_argument("path", nargs="?", help="repo root (default: cwd)")
    p_sync.set_defaults(func=_cmd_sync)

    p_check = sub.add_parser("check", help="validate docs (CI gate)")
    p_check.add_argument("path", nargs="?", help="repo root (default: cwd)")
    p_check.add_argument("--format", choices=["text", "github"], default="text",
                         help="output format")
    p_check.add_argument("--strict", action="store_true",
                         help="treat staleness warnings as errors")
    p_check.set_defaults(func=_cmd_check)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:  # noqa: BLE001 - top-level guard for a CLI
        print("codedoc: error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
