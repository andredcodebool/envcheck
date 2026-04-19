"""Reporting utilities for envcheck audit results."""

from __future__ import annotations

from typing import List

from envcheck.checker import CheckResult


ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"


def _color(text: str, code: str, use_color: bool) -> str:
    if not use_color:
        return text
    return f"{code}{text}{ANSI_RESET}"


def format_result(result: CheckResult, use_color: bool = True) -> str:
    """Format a single CheckResult into a human-readable string."""
    lines: List[str] = []

    header = f"[{result.service}]" if result.service else "[env]"
    if result.ok:
        status = _color("OK", ANSI_GREEN, use_color)
    else:
        status = _color("FAIL", ANSI_RED, use_color)

    lines.append(f"{_color(header, ANSI_BOLD, use_color)} {status}")

    if result.missing:
        label = _color("  Missing:", ANSI_YELLOW, use_color)
        lines.append(f"{label} {', '.join(sorted(result.missing))}")

    if result.extra:
        label = _color("  Extra:  ", ANSI_YELLOW, use_color)
        lines.append(f"{label} {', '.join(sorted(result.extra))}")

    return "\n".join(lines)


def format_summary(results: List[CheckResult], use_color: bool = True) -> str:
    """Format a list of CheckResults into a summary report."""
    sections = [format_result(r, use_color=use_color) for r in results]
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    failed = total - passed

    summary_line = f"\nSummary: {passed}/{total} passed"
    if failed:
        summary_line += _color(f", {failed} failed", ANSI_RED, use_color)
    else:
        summary_line += _color(" — all good", ANSI_GREEN, use_color)

    sections.append(summary_line)
    return "\n".join(sections)
