"""Main CLI entry-point for envcheck."""
from __future__ import annotations

import sys

import click

from envcheck.checker import check_env
from envcheck.config import ConfigError, find_config, get_profiles, load_config
from envcheck.loader import LoadError, load_from_env, load_from_file
from envcheck.reporter import format_result, format_summary
from envcheck.cli_audit import audit_group
from envcheck.cli_compare import compare_group
from envcheck.cli_template import template_group
from envcheck.cli_lint import lint_group
from envcheck.cli_transform import transform_group
from envcheck.cli_interpolate import interpolate_group


@click.group()
@click.version_option()
def cli() -> None:
    """envcheck — audit and validate environment variable configs."""


cli.add_command(audit_group)
cli.add_command(compare_group)
cli.add_command(template_group)
cli.add_command(lint_group)
cli.add_command(transform_group)
cli.add_command(interpolate_group)


@cli.command()
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--profile", default=None, help="Profile name from config.")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Config file.")
@click.option("--strict", is_flag=True, help="Fail on extra keys.")
def check(env_file: str, profile: str | None, config_path: str | None, strict: bool) -> None:
    """Check ENV_FILE against a profile's required keys."""
    try:
        cfg_path = config_path or find_config()
        cfg = load_config(cfg_path) if cfg_path else {}
        profiles = get_profiles(cfg)
    except ConfigError as exc:
        click.echo(f"Config error: {exc}", err=True)
        sys.exit(1)

    profile_name = profile or next(iter(profiles), None)
    prof = profiles.get(profile_name) if profile_name else None
    required = list(prof.required) if prof else []

    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"Load error: {exc}", err=True)
        sys.exit(1)

    result = check_env(env, required, strict=strict)
    click.echo(format_result(result, label=env_file))
    if not result.ok:
        sys.exit(1)


def main() -> None:  # pragma: no cover
    cli()
