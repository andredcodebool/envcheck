"""Snapshot: save and load environment variable snapshots for drift detection."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


class SnapshotError(Exception):
    pass


DEFAULT_SNAPSHOT_DIR = ".envcheck_snapshots"


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def save_snapshot(
    env: Dict[str, str],
    name: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> Path:
    """Persist *env* as a JSON snapshot under *snapshot_dir*/<name>/<timestamp>.json."""
    target = Path(snapshot_dir) / name
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{_timestamp()}.json"
    path.write_text(json.dumps(env, indent=2, sort_keys=True), encoding="utf-8")
    return path


def list_snapshots(name: str, snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> list[Path]:
    """Return snapshot paths for *name*, sorted oldest-first."""
    target = Path(snapshot_dir) / name
    if not target.exists():
        return []
    return sorted(target.glob("*.json"))


def load_snapshot(
    name: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
    index: int = -1,
) -> Dict[str, str]:
    """Load a snapshot by *index* (default: latest) for *name*."""
    snapshots = list_snapshots(name, snapshot_dir)
    if not snapshots:
        raise SnapshotError(f"No snapshots found for '{name}' in '{snapshot_dir}'")
    path = snapshots[index]
    return json.loads(path.read_text(encoding="utf-8"))


def latest_snapshot_path(
    name: str, snapshot_dir: str = DEFAULT_SNAPSHOT_DIR
) -> Optional[Path]:
    snapshots = list_snapshots(name, snapshot_dir)
    return snapshots[-1] if snapshots else None
