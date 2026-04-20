"""Main CLI entry-point for envcheck."""
from __future__ import annotations

import sys

import click

from envcheck.checker import check_env
from envcheck.config import ConfigError, find_config, get_profiles, load_config
from envcheck.loader import LoadError, load_from_file
from envcheck.reporter import format_result, format_summary
from envcheck.cli_audit import audit_group
from envcheck.cli_compare import compare_group
from envcheck.cli_template import template_group
from envcheck.cli_lint import lint_group
from envcheck.cli_transform import transform_group
from envcheck.cli_interpolate import interpolate_group
from envcheck.cli_validate import validate_group
from envcheck.cli_score import score_group


@click.group()
def cli() -> None:
    """envcheck — audit and validate environment variable configs."""


@cli.command()
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--profile", "profile_name", default="default", show_default=True)
@click.option("--config", "config_path", default=None, type=click.Path())
@click.option("--strict", is_flag=True, default=False, help="Fail on extra keys.")
def check(
    env_file: str,
    profile_name: str,
    config_path: str | None,
    strict: bool,
) -> None:
    """Check an env file against a profile."""
    try:
        cfg_path = config_path or find_config()
        cfg = load_config(cfg_path)
        profiles = get_profiles(cfg)
    except ConfigError as exc:
        click.echo(f"Config error: {exc}", err=True)
        sys.exit(2)

    profile = profiles.get(profile_name)
    if profile is None:
        click.echo(f"Profile '{profile_name}' not found.", err=True)
        sys.exit(2)

    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"Load error: {exc}", err=True)
        sys.exit(2)

    result = check_env(env, profile.required)
    click.echo(format_result(result, label=env_file))
    click.echo(format_summary([result]))

    if not result.ok or (strict and result.extra):
        sys.exit(1)


cli.add_command(audit_group, "audit")
cli.add_command(compare_group, "compare")
cli.add_command(template_group, "template")
cli.add_command(lint_group, "lint")
cli.add_command(transform_group, "transform")
cli.add_command(interpolate_group, "interpolate")
cli.add_command(validate_group, "validate")
cli.add_command(score_group, "score")


def main() -> None:
    cli()
