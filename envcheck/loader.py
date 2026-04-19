"""Load env configs from files, directories, or raw strings."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Optional

from envcheck.parser import parse_env_file, parse_env_string


class LoadError(Exception):
    """Raised when an env source cannot be loaded."""


def load_from_file(path: str | Path) -> Dict[str, str]:
    """Load env vars from a .env file."""
    p = Path(path)
    if not p.exists():
        raise LoadError(f"File not found: {p}")
    if not p.is_file():
        raise LoadError(f"Not a file: {p}")
    return parse_env_file(str(p))


def load_from_dir(directory: str | Path, pattern: str = "*.env") -> Dict[str, Dict[str, str]]:
    """Load all env files matching *pattern* inside *directory*.

    Returns a mapping of filename -> parsed vars.
    """
    d = Path(directory)
    if not d.is_dir():
        raise LoadError(f"Not a directory: {d}")
    result: Dict[str, Dict[str, str]] = {}
    for p in sorted(d.glob(pattern)):
        result[p.name] = parse_env_file(str(p))
    return result


def load_from_string(raw: str) -> Dict[str, str]:
    """Load env vars from a raw multi-line string."""
    return parse_env_string(raw)


def load_from_env(prefix: Optional[str] = None) -> Dict[str, str]:
    """Load vars from the current process environment.

    If *prefix* is given only vars starting with that prefix are included,
    and the prefix is stripped from the keys.
    """
    env = dict(os.environ)
    if prefix is None:
        return env
    stripped: Dict[str, str] = {}
    for k, v in env.items():
        if k.startswith(prefix):
            stripped[k[len(prefix):]] = v
    return stripped
