"""Load and validate the ``.codedoc.yml`` project configuration.

Every knob has a default, so a repo can adopt CodeDoc with an empty (or
absent) config file and still get sensible behaviour. The config controls
where docs live, which agent adapter files to generate, and how strict the
``check`` command is.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from . import _yaml

CONFIG_FILENAME = ".codedoc.yml"

# Adapter files fan the single source of truth (AGENTS.md) out to agents that
# insist on their own filename. Each entry: (config-key, output-path, kind).
#   kind "pointer"  -> a short markdown stub that redirects to AGENTS.md
#   kind "mdc"      -> Cursor .mdc rule (needs its own front-matter)
ADAPTER_TARGETS = {
    "claude": {"path": "CLAUDE.md", "kind": "pointer", "label": "Claude Code"},
    "hermes": {"path": ".hermes.md", "kind": "pointer", "label": "Hermes"},
    "copilot": {
        "path": ".github/copilot-instructions.md",
        "kind": "pointer",
        "label": "GitHub Copilot",
    },
    "cursor": {
        "path": ".cursor/rules/codedoc.mdc",
        "kind": "mdc",
        "label": "Cursor",
    },
    "windsurf": {
        "path": ".windsurf/rules/codedoc.md",
        "kind": "pointer",
        "label": "Windsurf",
    },
    "gemini": {"path": "GEMINI.md", "kind": "pointer", "label": "Gemini CLI"},
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "docs_dir": "docs",
    "instructions_file": "AGENTS.md",
    # Which adapter files to generate & keep in sync. All on by default —
    # an unused pointer file is harmless, a missing one loses an agent.
    "adapters": ["claude", "hermes", "copilot", "cursor", "windsurf", "gemini"],
    # Front-matter keys every doc must define.
    "required_frontmatter": ["title", "status"],
    # Allowed values for the "status" key.
    "statuses": ["current", "draft", "deprecated"],
    "check": {
        # Fail (vs warn) when a doc references a related_code path that no
        # longer exists on disk.
        "orphaned_code_is_error": True,
        # Fail when an internal docs link points at a missing file.
        "broken_links_is_error": True,
        # Fail when a generated adapter/llms.txt is out of date.
        "drift_is_error": True,
        # Warn when a related_code file is newer than its doc (possible
        # staleness). Set to "error" to block PRs, "off" to disable.
        "staleness": "warn",
        # Glob-style path prefixes to ignore when validating related_code.
        "ignore_code_paths": [],
    },
}


class ConfigError(ValueError):
    """Raised when ``.codedoc.yml`` is present but invalid."""


def _merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load(root: str) -> Dict[str, Any]:
    """Load merged config from ``<root>/.codedoc.yml`` (or defaults)."""
    path = os.path.join(root, CONFIG_FILENAME)
    if not os.path.exists(path):
        return _clone(DEFAULT_CONFIG)
    with open(path, "r", encoding="utf-8") as handle:
        raw = _yaml.parse(handle.read())
    if raw is None:
        return _clone(DEFAULT_CONFIG)
    if not isinstance(raw, dict):
        raise ConfigError("%s must be a mapping at the top level" % CONFIG_FILENAME)
    merged = _merge(DEFAULT_CONFIG, raw)
    _validate(merged)
    return merged


def _validate(cfg: Dict[str, Any]) -> None:
    for name in cfg.get("adapters", []):
        if name not in ADAPTER_TARGETS:
            raise ConfigError(
                "unknown adapter %r (known: %s)"
                % (name, ", ".join(sorted(ADAPTER_TARGETS)))
            )
    staleness = cfg["check"].get("staleness")
    if staleness not in ("off", "warn", "error"):
        raise ConfigError("check.staleness must be off|warn|error, got %r" % staleness)


def _clone(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: _clone(v) for k, v in data.items()}
    if isinstance(data, list):
        return [_clone(v) for v in data]
    return data


def adapters_for(cfg: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return resolved adapter target descriptors for the enabled adapters."""
    result = []
    for name in cfg.get("adapters", []):
        target = dict(ADAPTER_TARGETS[name])
        target["name"] = name
        result.append(target)
    return result
