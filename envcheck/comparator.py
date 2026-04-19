"""Compare two env sets against a profile and produce a CompareReport."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envcheck.checker import check_env, CheckResult
from envcheck.differ import diff_envs, DiffResult
from envcheck.profile import Profile


@dataclass
class CompareReport:
    profile_name: str
    left_label: str
    right_label: str
    left_result: CheckResult
    right_result: CheckResult
    diff: DiffResult
    left_env: Dict[str, str] = field(default_factory=dict)
    right_env: Dict[str, str] = field(default_factory=dict)


def compare(
    left: Dict[str, str],
    right: Dict[str, str],
    profile: Profile,
    left_label: str = "left",
    right_label: str = "right",
) -> CompareReport:
    """Check both envs against *profile* and diff them."""
    left_result = check_env(left, profile.required, profile.optional)
    right_result = check_env(right, profile.required, profile.optional)
    diff = diff_envs(left, right)
    return CompareReport(
        profile_name=profile.name,
        left_label=left_label,
        right_label=right_label,
        left_result=left_result,
        right_result=right_result,
        diff=diff,
        left_env=left,
        right_env=right,
    )


def format_compare(report: CompareReport, *, color: bool = True) -> str:
    from envcheck.reporter import format_result, _color
    from envcheck.differ import format_diff

    lines: List[str] = []
    header = f"=== Compare: {report.left_label}  vs  {report.right_label}  [profile: {report.profile_name}] ==="
    lines.append(_color(header, "cyan") if color else header)
    lines.append(f"\n-- {report.left_label} --")
    lines.append(format_result(report.left_result, label=report.left_label, color=color))
    lines.append(f"\n-- {report.right_label} --")
    lines.append(format_result(report.right_result, label=report.right_label, color=color))
    lines.append("\n-- Diff --")
    lines.append(format_diff(report.diff, left_label=report.left_label, right_label=report.right_label))
    return "\n".join(lines)
