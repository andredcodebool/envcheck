"""Audit log: record check runs with timestamp and result summary."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

DEFAULT_AUDIT_DIR = Path(".envcheck") / "audit"


@dataclass
class AuditEntry:
    timestamp: str
    profile: str
    source: str
    passed: bool
    missing: List[str] = field(default_factory=list)
    extra: List[str] = field(default_factory=list)
    note: Optional[str] = None


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def record(
    entry: AuditEntry,
    audit_dir: Path = DEFAULT_AUDIT_DIR,
) -> Path:
    """Persist an audit entry as a JSON file and return its path."""
    audit_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{entry.timestamp}_{entry.profile}.json"
    path = audit_dir / filename
    path.write_text(json.dumps(asdict(entry), indent=2))
    return path


def list_entries(audit_dir: Path = DEFAULT_AUDIT_DIR) -> List[AuditEntry]:
    """Return all audit entries sorted oldest-first."""
    if not audit_dir.exists():
        return []
    entries = []
    for p in sorted(audit_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text())
            entries.append(AuditEntry(**data))
        except Exception:
            continue
    return entries


def entry_from_check(profile: str, source: str, result) -> AuditEntry:
    """Build an AuditEntry from a checker.CheckResult."""
    return AuditEntry(
        timestamp=_now(),
        profile=profile,
        source=source,
        passed=result.ok,
        missing=list(result.missing),
        extra=list(result.extra),
    )
