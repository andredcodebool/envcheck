"""Drift detection: compare current env against a saved snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envcheck.snapshot import load_snapshot, save_snapshot, SnapshotError


@dataclass
class DriftReport:
    name: str
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def detect_drift(
    current: Dict[str, str],
    name: str,
    snapshot_dir: str = ".envcheck_snapshots",
) -> DriftReport:
    """Compare *current* env against the latest snapshot for *name*.

    Raises SnapshotError if no snapshot exists.
    """
    baseline = load_snapshot(name, snapshot_dir=snapshot_dir)
    report = DriftReport(name=name)

    baseline_keys = set(baseline)
    current_keys = set(current)

    report.added = sorted(current_keys - baseline_keys)
    report.removed = sorted(baseline_keys - current_keys)
    report.changed = sorted(
        k for k in baseline_keys & current_keys if baseline[k] != current[k]
    )
    return report


def format_drift(report: DriftReport) -> str:
    if not report.has_drift:
        return f"[OK] '{report.name}': no drift detected."

    lines = [f"[DRIFT] '{report.name}':"]
    for k in report.added:
        lines.append(f"  + {k}  (added)")
    for k in report.removed:
        lines.append(f"  - {k}  (removed)")
    for k in report.changed:
        lines.append(f"  ~ {k}  (changed)")
    return "\n".join(lines)
