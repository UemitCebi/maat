"""A tiny YAML-subset parser and emitter (stdlib-only).

CodeDoc is intentionally dependency-free so it can be vendored into any
repository and run under a bare Python interpreter. That rules out PyYAML,
so this module implements just enough of YAML to cover:

* scalars: ``str``, ``int``, ``float``, ``bool``, ``null``
* quoted strings: ``"..."`` and ``'...'``
* flow sequences: ``[a, b, c]``
* block sequences::

      key:
        - one
        - two

* nested mappings by indentation (two spaces per level by convention)
* ``#`` comments and blank lines

It is NOT a general YAML implementation. It rejects constructs it does not
understand with a :class:`YamlError` rather than guessing, because silent
misparsing of documentation metadata is worse than a loud failure.
"""

from __future__ import annotations

from typing import Any, List, Tuple


class YamlError(ValueError):
    """Raised when the input uses YAML features this parser does not support."""


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def _strip_comment(line: str) -> str:
    """Remove a trailing ``#`` comment that is not inside quotes."""
    in_single = in_double = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            # A '#' only starts a comment when preceded by whitespace or BOL.
            if i == 0 or line[i - 1] in " \t":
                return line[:i]
    return line


def _scalar(raw: str) -> Any:
    """Coerce a scalar token into a Python value."""
    s = raw.strip()
    if not s:
        return ""
    if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
        return s[1:-1]
    low = s.lower()
    if low in ("null", "~", "none"):
        return None
    if low == "true":
        return True
    if low == "false":
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _flow_list(raw: str) -> List[Any]:
    """Parse ``[a, b, c]`` respecting quotes."""
    inner = raw.strip()[1:-1]
    if not inner.strip():
        return []
    items, buf, in_s, in_d = [], "", False, False
    for ch in inner:
        if ch == "'" and not in_d:
            in_s = not in_s
            buf += ch
        elif ch == '"' and not in_s:
            in_d = not in_d
            buf += ch
        elif ch == "," and not in_s and not in_d:
            items.append(_scalar(buf))
            buf = ""
        else:
            buf += ch
    if buf.strip():
        items.append(_scalar(buf))
    return items


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


class _Lines:
    """A rewindable iterator over (indent, text) tuples for non-blank lines."""

    def __init__(self, text: str) -> None:
        self.rows: List[Tuple[int, str]] = []
        for raw in text.splitlines():
            if "\t" in (raw[: _indent(raw) + 1]):
                raise YamlError("tabs are not allowed for indentation")
            stripped = _strip_comment(raw).rstrip()
            if not stripped.strip():
                continue
            self.rows.append((_indent(stripped), stripped.strip()))
        self.pos = 0

    def peek(self) -> Tuple[int, str] | None:
        return self.rows[self.pos] if self.pos < len(self.rows) else None

    def next(self) -> Tuple[int, str]:
        row = self.rows[self.pos]
        self.pos += 1
        return row


def _parse_block(lines: _Lines, indent: int) -> Any:
    """Parse a mapping or sequence whose items sit at column ``indent``."""
    peek = lines.peek()
    if peek is None:
        return None

    if peek[1].startswith("- "):
        return _parse_sequence(lines, indent)
    return _parse_mapping(lines, indent)


def _parse_sequence(lines: _Lines, indent: int) -> List[Any]:
    seq: List[Any] = []
    while True:
        peek = lines.peek()
        if peek is None or peek[0] != indent or not peek[1].startswith("- "):
            break
        _, text = lines.next()
        item = text[2:].strip()
        if item:
            seq.append(_scalar(item) if not item.startswith("[") else _flow_list(item))
        else:
            seq.append(_parse_block(lines, indent + 2))
    return seq


def _parse_mapping(lines: _Lines, indent: int) -> dict:
    mapping: dict = {}
    while True:
        peek = lines.peek()
        if peek is None or peek[0] != indent:
            break
        if peek[1].startswith("- "):
            break
        _, text = lines.next()
        if ":" not in text:
            raise YamlError("expected 'key: value', got: %r" % text)
        key, _, rest = text.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "":
            child = lines.peek()
            if child is not None and child[0] > indent:
                mapping[key] = _parse_block(lines, child[0])
            else:
                mapping[key] = None
        elif rest.startswith("["):
            mapping[key] = _flow_list(rest)
        else:
            mapping[key] = _scalar(rest)
    return mapping


def parse(text: str) -> Any:
    """Parse a YAML-subset document into Python objects."""
    lines = _Lines(text)
    first = lines.peek()
    if first is None:
        return {}
    return _parse_block(lines, first[0])


# --------------------------------------------------------------------------- #
# Emitting
# --------------------------------------------------------------------------- #

def _needs_quote(s: str) -> bool:
    if s == "":
        return True
    if s.lower() in ("null", "true", "false", "none", "~", "yes", "no"):
        return True
    if s[0] in "!&*?|>%@`\"'#,[]{}" or s[0] in " ":
        return True
    if ": " in s or s.endswith(":") or " #" in s:
        return True
    return False


def _emit_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    if _needs_quote(s):
        return '"%s"' % s.replace('"', '\\"')
    return s


def emit(data: Any, indent: int = 0) -> str:
    """Serialize Python objects back to the YAML subset. Deterministic order."""
    pad = " " * indent
    out: List[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and value:
                out.append("%s%s:" % (pad, key))
                out.append(emit(value, indent + 2))
            elif isinstance(value, list) and value:
                out.append("%s%s:" % (pad, key))
                for item in value:
                    if isinstance(item, (dict, list)):
                        out.append("%s-" % (" " * (indent + 2)))
                        out.append(emit(item, indent + 4))
                    else:
                        out.append("%s- %s" % (" " * (indent + 2), _emit_scalar(item)))
            elif isinstance(value, list):
                out.append("%s%s: []" % (pad, key))
            else:
                out.append("%s%s: %s" % (pad, key, _emit_scalar(value)))
    elif isinstance(data, list):
        for item in data:
            out.append("%s- %s" % (pad, _emit_scalar(item)))
    else:
        out.append("%s%s" % (pad, _emit_scalar(data)))
    return "\n".join(out)
