"""Health scoring for environment variable sets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from envcheck.checker import CheckResult
from envcheck.linter import LintReport
from envcheck.validator import ValidationReport


@dataclass
class ScoreReport:
    total: int
    passed: int
    deductions: list[tuple[str, int]] = field(default_factory=list)

    @property
    def score(self) -> int:
        lost = sum(pts for _, pts in self.deductions)
        return max(0, self.total - lost)

    @property
    def grade(self) -> str:
        pct = self.score / self.total if self.total else 0
        if pct >= 0.9:
            return "A"
        if pct >= 0.75:
            return "B"
        if pct >= 0.6:
            return "C"
        if pct >= 0.4:
            return "D"
        return "F"


def score_env(
    check: CheckResult | None = None,
    lint: LintReport | None = None,
    validation: ValidationReport | None = None,
    base: int = 100,
) -> ScoreReport:
    """Compute a composite health score from check/lint/validation results."""
    deductions: list[tuple[str, int]] = []

    if check is not None:
        missing_penalty = len(check.missing) * 10
        if missing_penalty:
            deductions.append((f"{len(check.missing)} missing required key(s)", missing_penalty))

    if lint is not None:
        errors = [i for i in lint.issues if i.severity == "error"]
        warns = [i for i in lint.issues if i.severity == "warning"]
        if errors:
            deductions.append((f"{len(errors)} lint error(s)", len(errors) * 5))
        if warns:
            deductions.append((f"{len(warns)} lint warning(s)", len(warns) * 2))

    if validation is not None:
        invalid = [i for i in validation.issues if not i.passed]
        if invalid:
            deductions.append((f"{len(invalid)} validation failure(s)", len(invalid) * 8))

    passed = base - sum(pts for _, pts in deductions)
    return ScoreReport(total=base, passed=max(0, passed), deductions=deductions)


def format_score(report: ScoreReport) -> str:
    """Return a human-readable score summary."""
    lines = [
        f"Health Score: {report.score}/{report.total}  [{report.grade}]",
    ]
    if report.deductions:
        lines.append("Deductions:")
        for reason, pts in report.deductions:
            lines.append(f"  -{pts:>3}  {reason}")
    else:
        lines.append("  No issues found — perfect score!")
    return "\n".join(lines)
