"""Pin environment variable values to a named snapshot for drift detection."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


class PinError(Exception):
    """Raised when a pin operation fails."""


@dataclass
class PinReport:
    name: str
    pinned: Dict[str, str]
    drifted: List[str] = field(default_factory=list)
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not (self.drifted or self.new_keys or self.removed_keys)


def _pin_path(pin_dir: Path, name: str) -> Path:
    return pin_dir / f"{name}.pin.json"


def save_pin(env: Dict[str, str], name: str, pin_dir: Path) -> Path:
    """Persist *env* as a named pin inside *pin_dir*."""
    pin_dir.mkdir(parents=True, exist_ok=True)
    path = _pin_path(pin_dir, name)
    path.write_text(json.dumps(env, indent=2, sort_keys=True), encoding="utf-8")
    return path


def load_pin(name: str, pin_dir: Path) -> Dict[str, str]:
    """Load a previously saved pin by *name*."""
    path = _pin_path(pin_dir, name)
    if not path.exists():
        raise PinError(f"Pin '{name}' not found in {pin_dir}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PinError(f"Corrupt pin file '{path}': {exc}") from exc


def list_pins(pin_dir: Path) -> List[str]:
    """Return sorted list of pin names stored in *pin_dir*."""
    if not pin_dir.exists():
        return []
    return sorted(p.stem.replace(".pin", "") for p in pin_dir.glob("*.pin.json"))


def compare_pin(env: Dict[str, str], name: str, pin_dir: Path) -> PinReport:
    """Compare *env* against the saved pin *name* and return a PinReport."""
    pinned = load_pin(name, pin_dir)
    current_keys = set(env)
    pinned_keys = set(pinned)

    drifted = [k for k in current_keys & pinned_keys if env[k] != pinned[k]]
    new_keys = sorted(current_keys - pinned_keys)
    removed_keys = sorted(pinned_keys - current_keys)

    return PinReport(
        name=name,
        pinned=pinned,
        drifted=sorted(drifted),
        new_keys=new_keys,
        removed_keys=removed_keys,
    )


def format_pin_report(report: PinReport) -> str:
    """Return a human-readable summary of *report*."""
    lines: List[str] = [f"Pin: {report.name}"]
    if report.clean:
        lines.append("  ✓ No drift detected.")
        return "\n".join(lines)
    if report.drifted:
        lines.append("  ~ Changed values:")
        for k in report.drifted:
            lines.append(f"      {k}")
    if report.new_keys:
        lines.append("  + New keys:")
        for k in report.new_keys:
            lines.append(f"      {k}")
    if report.removed_keys:
        lines.append("  - Removed keys:")
        for k in report.removed_keys:
            lines.append(f"      {k}")
    return "\n".join(lines)
