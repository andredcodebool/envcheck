"""Lint individual env keys for naming conventions and common issues."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Dict

_UPPER_SNAKE = re.compile(r'^[A-Z][A-Z0-9_]*$')
_LEADING_DIGIT = re.compile(r'^[0-9]')
_WHITESPACE_VAL = re.compile(r'^\s|\s$')


@dataclass
class LintIssue:
    key: str
    code: str
    message: str


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0


def _lint_key(key: str) -> List[LintIssue]:
    issues: List[LintIssue] = []
    if not _UPPER_SNAKE.match(key):
        issues.append(LintIssue(key, "E001", f"Key '{key}' should be UPPER_SNAKE_CASE"))
    if _LEADING_DIGIT.match(key):
        issues.append(LintIssue(key, "E002", f"Key '{key}' must not start with a digit"))
    if '__' in key:
        issues.append(LintIssue(key, "W001", f"Key '{key}' contains double underscore"))
    return issues


def _lint_value(key: str, value: str) -> List[LintIssue]:
    issues: List[LintIssue] = []
    if _WHITESPACE_VAL.search(value):
        issues.append(LintIssue(key, "W002", f"Value for '{key}' has leading or trailing whitespace"))
    if value == "":
        issues.append(LintIssue(key, "W003", f"Value for '{key}' is empty"))
    return issues


def lint_env(env: Dict[str, str]) -> LintReport:
    """Run all lint checks on an env mapping and return a LintReport."""
    issues: List[LintIssue] = []
    for key, value in env.items():
        issues.extend(_lint_key(key))
        issues.extend(_lint_value(key, value))
    return LintReport(issues=issues)


def format_lint(report: LintReport, *, color: bool = True) -> str:
    if report.ok:
        return "\033[32m✔ No lint issues found\033[0m" if color else "✔ No lint issues found"
    lines = []
    for issue in report.issues:
        prefix = "[E]" if issue.code.startswith("E") else "[W]"
        if color:
            c = "\033[31m" if issue.code.startswith("E") else "\033[33m"
            lines.append(f"{c}{prefix} {issue.code}: {issue.message}\033[0m")
        else:
            lines.append(f"{prefix} {issue.code}: {issue.message}")
    return "\n".join(lines)
