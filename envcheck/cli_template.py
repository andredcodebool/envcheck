"""CLI sub-commands for template generation."""
from __future__ import annotations

import sys

import click

from envcheck.config import get_profiles, load_config
from envcheck.loader import load_from_file
from envcheck.templater import template_from_keys, template_from_profile, write_template


@click.group("template")
def template_group() -> None:
    """Generate .env.example template files."""


@template_group.command("from-profile")
@click.argument("profile_name")
@click.option("--config", "config_path", default=None, help="Path to envcheck config.")
@click.option("--output", "-o", default=None, help="Output file (default: stdout).")
def from_profile_cmd(profile_name: str, config_path: str | None, output: str | None) -> None:
    """Generate a template from a named profile."""
    try:
        cfg = load_config(config_path)
        profiles = get_profiles(cfg)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error loading config: {exc}", err=True)
        sys.exit(1)

    profile = profiles.get(profile_name)
    if profile is None:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        sys.exit(1)

    content = from_profile_cmd_inner(profile)
    _emit(content, output)


def from_profile_cmd_inner(profile):  # extracted for testability
    return template_from_profile(profile)


@template_group.command("from-file")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output file (default: stdout).")
@click.option("--no-redact", is_flag=True, default=False)
def from_file_cmd(env_file: str, output: str | None, no_redact: bool) -> None:
    """Generate a template from an existing .env file (values stripped)."""
    try:
        mapping = load_from_file(env_file)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error reading file: {exc}", err=True)
        sys.exit(1)

    content = template_from_keys(mapping.keys(), redact=not no_redact)
    _emit(content, output)


def _emit(content: str, output: str | None) -> None:
    if output:
        write_template(content, output)
        click.echo(f"Template written to {output}")
    else:
        click.echo(content, nl=False)
