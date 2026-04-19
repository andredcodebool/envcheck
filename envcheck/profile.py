"""Profile: a named set of required (and optional) keys for a service."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Profile:
    """Describes the expected env-var shape for a service or component."""

    name: str
    required: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    description: str = ""

    def all_known(self) -> List[str]:
        """Return all keys declared in this profile."""
        return list(self.required) + list(self.optional)


def profile_from_dict(data: Dict) -> Profile:
    """Build a Profile from a plain dictionary (e.g. parsed from TOML/JSON)."""
    return Profile(
        name=data["name"],
        required=list(data.get("required", [])),
        optional=list(data.get("optional", [])),
        description=data.get("description", ""),
    )


def load_profiles(profiles_data: List[Dict]) -> Dict[str, Profile]:
    """Build a name-keyed mapping of profiles from a list of dicts."""
    result: Dict[str, Profile] = {}
    for entry in profiles_data:
        p = profile_from_dict(entry)
        result[p.name] = p
    return result
