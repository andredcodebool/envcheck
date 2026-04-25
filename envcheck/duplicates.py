"""Detect duplicate keys within an env file or across multiple env mappings."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class DuplicateReport:
    """Result of a duplicate-key scan."""

    # Keys that appear more than once within a single source (intra-source)
    intra: Dict[str, int] = field(default_factory=dict)  # key -> count
    # Keys that appear in more than one source (inter-source)
    inter: List[str] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return bool(self.intra) or bool(self.inter)


def find_intra_duplicates(lines: List[str]) -> Dict[str, int]:
    """Return keys that appear more than once in a raw list of 'KEY=VALUE' lines."""
    counts: Dict[str, int] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key = stripped.split("=", 1)[0].strip()
        counts[key] = counts.get(key, 0) + 1
    return {k: v for k, v in counts.items() if v > 1}


def find_inter_duplicates(envs: List[Dict[str, str]]) -> List[str]:
    """Return keys present in more than one of the supplied env mappings."""
    seen: Dict[str, int] = {}
    for env in envs:
        for key in env:
            seen[key] = seen.get(key, 0) + 1
    return sorted(k for k, v in seen.items() if v > 1)


def scan(
    lines: List[str] | None = None,
    envs: List[Dict[str, str]] | None = None,
) -> DuplicateReport:
    """Convenience wrapper: run intra and/or inter duplicate detection."""
    intra = find_intra_duplicates(lines) if lines is not None else {}
    inter = find_inter_duplicates(envs) if envs is not None else []
    return DuplicateReport(intra=intra, inter=inter)


def format_report(report: DuplicateReport, *, color: bool = True) -> str:
    """Return a human-readable summary of the duplicate report."""
    RED = "\033[31m" if color else ""
    YELLOW = "\033[33m" if color else ""
    RESET = "\033[0m" if color else ""

    if not report.has_duplicates:
        return f"{YELLOW}No duplicate keys found.{RESET}"

    lines: List[str] = []
    if report.intra:
        lines.append(f"{RED}Intra-source duplicates:{RESET}")
        for key, count in sorted(report.intra.items()):
            lines.append(f"  {key}  ({count}x)")
    if report.inter:
        lines.append(f"{RED}Inter-source duplicates:{RESET}")
        for key in report.inter:
            lines.append(f"  {key}")
    return "\n".join(lines)
