"""Patch (update/add/remove) keys in an env mapping and write results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PatchReport:
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    unchanged: List[str] = field(default_factory=list)


def apply_patch(
    env: Dict[str, str],
    *,
    set_keys: Optional[Dict[str, str]] = None,
    remove_keys: Optional[List[str]] = None,
) -> tuple[Dict[str, str], PatchReport]:
    """Return a new env dict with patches applied plus a PatchReport."""
    result = dict(env)
    report = PatchReport()

    for key, value in (set_keys or {}).items():
        if key in result:
            if result[key] != value:
                result[key] = value
                report.updated.append(key)
            else:
                report.unchanged.append(key)
        else:
            result[key] = value
            report.added.append(key)

    for key in remove_keys or []:
        if key in result:
            del result[key]
            report.removed.append(key)

    for key in result:
        if key not in (set_keys or {}) and key not in (remove_keys or []):
            if key not in report.unchanged:
                report.unchanged.append(key)

    return result, report


def format_patch(report: PatchReport) -> str:
    """Return a human-readable summary of a PatchReport."""
    lines: List[str] = []
    for key in sorted(report.added):
        lines.append(f"  + {key}  [added]")
    for key in sorted(report.updated):
        lines.append(f"  ~ {key}  [updated]")
    for key in sorted(report.removed):
        lines.append(f"  - {key}  [removed]")
    total = len(report.added) + len(report.updated) + len(report.removed)
    lines.append(f"\n{total} change(s): {len(report.added)} added, "
                 f"{len(report.updated)} updated, {len(report.removed)} removed.")
    return "\n".join(lines)
