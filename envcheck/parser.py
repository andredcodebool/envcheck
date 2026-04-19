"""Parser for .env and .env.example files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_RE = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$")
COMMENT_RE = re.compile(r"^\s*#")


def parse_env_file(path: Path) -> Dict[str, Optional[str]]:
    """Parse an env file and return a dict of key -> value.

    Values are None when the variable is declared without a value (e.g. in
    .env.example files where the value is intentionally left blank).
    """
    result: Dict[str, Optional[str]] = {}

    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()
            if not line or COMMENT_RE.match(line):
                continue
            m = ENV_LINE_RE.match(line)
            if m:
                key = m.group("key")
                value: Optional[str] = m.group("value").strip() or None
                result[key] = value

    return result


def parse_env_string(content: str) -> Dict[str, Optional[str]]:
    """Parse env content from a string (useful for testing)."""
    result: Dict[str, Optional[str]] = {}

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or COMMENT_RE.match(line):
            continue
        m = ENV_LINE_RE.match(line)
        if m:
            key = m.group("key")
            value: Optional[str] = m.group("value").strip() or None
            result[key] = value

    return result
