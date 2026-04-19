"""Read envcheck configuration from a TOML file."""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Dict, List, Optional

from envcheck.profile import Profile, load_profiles

DEFAULT_CONFIG_NAMES = ["envcheck.toml", ".envcheck.toml"]


class ConfigError(Exception):
    """Raised for invalid or missing configuration."""


def find_config(start: Optional[Path] = None) -> Optional[Path]:
    """Walk up from *start* (default: cwd) looking for a config file."""
    directory = Path(start or Path.cwd()).resolve()
    for parent in [directory, *directory.parents]:
        for name in DEFAULT_CONFIG_NAMES:
            candidate = parent / name
            if candidate.is_file():
                return candidate
    return None


def load_config(path: Optional[str | Path] = None) -> Dict:
    """Load and return raw config dict from *path* or auto-discovered file."""
    if path is None:
        path = find_config()
    if path is None:
        raise ConfigError("No envcheck.toml config file found.")
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def get_profiles(path: Optional[str | Path] = None) -> Dict[str, Profile]:
    """Load profiles declared in the config file."""
    raw = load_config(path)
    profiles_data = raw.get("profiles", [])
    if not profiles_data:
        raise ConfigError("No [profiles] section found in config.")
    return load_profiles(profiles_data)
