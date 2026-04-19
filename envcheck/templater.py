"""Generate .env.example templates from profiles or existing env files."""
from __future__ import annotations

from typing import Iterable

from envcheck.profile import Profile
from envcheck.redactor import is_sensitive

_PLACEHOLDER = "your_value_here"
_SENSITIVE_PLACEHOLDER = "****"


def _placeholder(key: str) -> str:
    return _SENSITIVE_PLACEHOLDER if is_sensitive(key) else _PLACEHOLDER


def template_from_profile(profile: Profile) -> str:
    """Return an .env.example string for all required + optional keys."""
    lines: list[str] = [f"# envcheck template — profile: {profile.name}", ""]
    if profile.required:
        lines.append("# Required")
        for key in sorted(profile.required):
            lines.append(f"{key}={_placeholder(key)}")
        lines.append("")
    if profile.optional:
        lines.append("# Optional")
        for key in sorted(profile.optional):
            lines.append(f"# {key}={_placeholder(key)}")
        lines.append("")
    return "\n".join(lines)


def template_from_keys(keys: Iterable[str], *, redact: bool = True) -> str:
    """Return an .env.example string from an arbitrary collection of keys."""
    lines: list[str] = []
    for key in sorted(keys):
        ph = _placeholder(key) if redact else _PLACEHOLDER
        lines.append(f"{key}={ph}")
    return "\n".join(lines) + "\n" if lines else ""


def write_template(content: str, path: str) -> None:
    """Write template content to *path*."""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
