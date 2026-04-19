"""CLI sub-commands for comparing two env sources."""
from __future__ import annotations

import sys
import click

from envcheck.loader import load_from_file, load_from_env, LoadError
from envcheck.config import load_config, get_profiles, ConfigError
from envcheck.comparator import compare, format_compare


@click.group("compare")
def compare_group() -> None:
    """Compare two environment sources against a profile."""


@compare_group.command("files")
@click.argument("left_file", type=click.Path(exists=True))
@click.argument("right_file", type=click.Path(exists=True))
@click.option("--profile", "profile_name", default=None, help="Profile name from envcheck config.")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Path to envcheck config.")
@click.option("--no-color", is_flag=True, default=False)
def files_cmd(
    left_file: str,
    right_file: str,
    profile_name: str | None,
    config_path: str | None,
    no_color: bool,
) -> None:
    """Compare LEFT_FILE and RIGHT_FILE env files."""
    try:
        left = load_from_file(left_file)
        right = load_from_file(right_file)
    except LoadError as exc:
        click.echo(f"Load error: {exc}", err=True)
        sys.exit(1)

    profile = _resolve_profile(profile_name, config_path)
    report = compare(left, right, profile, left_label=left_file, right_label=right_file)
    click.echo(format_compare(report, color=not no_color))
    if not (report.left_result.ok and report.right_result.ok):
        sys.exit(1)


@compare_group.command("env-vs-file")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--profile", "profile_name", default=None)
@click.option("--config", "config_path", default=None, type=click.Path())
@click.option("--no-color", is_flag=True, default=False)
def env_vs_file_cmd(
    env_file: str,
    profile_name: str | None,
    config_path: str | None,
    no_color: bool,
) -> None:
    """Compare the live process environment against ENV_FILE."""
    try:
        file_env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"Load error: {exc}", err=True)
        sys.exit(1)

    live_env = load_from_env()
    profile = _resolve_profile(profile_name, config_path)
    report = compare(live_env, file_env, profile, left_label="live", right_label=env_file)
    click.echo(format_compare(report, color=not no_color))
    if not (report.left_result.ok and report.right_result.ok):
        sys.exit(1)


def _resolve_profile(name: str | None, config_path: str | None):
    from envcheck.profile import Profile
    try:
        cfg = load_config(config_path)
        profiles = get_profiles(cfg)
        if name and name in profiles:
            return profiles[name]
        if profiles:
            return next(iter(profiles.values()))
    except (ConfigError, Exception):
        pass
    return Profile(name="default", required=[], optional=[])
