"""Freeze and restore environment variable sets.

A 'freeze' captures the current env dict to a named, portable JSON file.
A 'thaw' reads it back and optionally writes it as a .env file.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class FreezeError(Exception):
    """Raised when a freeze/thaw operation fails."""


@dataclass
class FreezeRecord:
    name: str
    env: Dict[str, str]
    keys: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.keys = sorted(self.env.keys())


def freeze(env: Dict[str, str], name: str, dest_dir: Path) -> Path:
    """Serialise *env* to ``<dest_dir>/<name>.freeze.json``.

    Returns the path of the written file.
    """
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    record = FreezeRecord(name=name, env=env)
    payload = {
        "name": record.name,
        "keys": record.keys,
        "env": record.env,
    }
    out = dest_dir / f"{name}.freeze.json"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return out


def thaw(src: Path) -> FreezeRecord:
    """Load a freeze file and return a :class:`FreezeRecord`."""
    src = Path(src)
    if not src.exists():
        raise FreezeError(f"freeze file not found: {src}")
    try:
        payload = json.loads(src.read_text())
    except json.JSONDecodeError as exc:
        raise FreezeError(f"invalid freeze file: {exc}") from exc
    return FreezeRecord(name=payload["name"], env=payload["env"])


def list_freezes(directory: Path) -> List[Path]:
    """Return all freeze files in *directory*, sorted by name."""
    directory = Path(directory)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.freeze.json"))


def write_env_file(record: FreezeRecord, dest: Path) -> None:
    """Write *record.env* as a .env-style file to *dest*."""
    lines = [f"{k}={v}\n" for k, v in sorted(record.env.items())]
    Path(dest).write_text("".join(lines))
