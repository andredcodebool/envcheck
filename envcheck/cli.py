"""CLI entry point for envcheck."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import click

from .checker import check_env
from .config import ConfigError, find_config, get_profiles, load_config
from .loader import LoadError, load_from_dir, load_from_env, load_from_file
from .reporter import format_result, format_summary


@click.group()
def cli() -> None:
    """envcheck — audit and validate environment variable configs."""


@cli.command()
@click.option("--env-file", "-e", default=None, help="Path to .env file to validate.")
@click.option("--env-dir", "-d", default=None, help="Directory of .env files.")
@click.option("--profile", "-p", multiple=True, help="Profile(s) to validate against.")
@click.option("--config", "-c", default=None, help="Path to envcheck config file.")
@click.option("--use-process-env", is_flag=True, default=False, help="Use current process environment.")
@click.option("--strict", is_flag=True, default=False, help="Fail on extra keys too.")
def check(
    env_file: str | None,
    env_dir: str | None,
    profile: tuple[str, ...],
    config: str | None,
    use_process_env: bool,
    strict: bool,
) -> None:
    """Validate an environment against one or more profiles."""
    try:
        config_path = Path(config) if config else find_config()
        cfg = load_config(config_path) if config_path else {}
        profiles = get_profiles(cfg)
    except ConfigError as exc:
        click.echo(f"Config error: {exc}", err=True)
        sys.exit(2)

    try:
        if use_process_env:
            env = load_from_env()
        elif env_dir:
            env = load_from_dir(Path(env_dir))
        elif env_file:
            env = load_from_file(Path(env_file))
        else:
            env = load_from_env()
    except LoadError as exc:
        click.echo(f"Load error: {exc}", err=True)
        sys.exit(2)

    selected = [p for p in profiles if not profile or p.name in profile]
    if not selected:
        click.echo("No profiles found to check against.", err=True)
        sys.exit(2)

    results = [check_env(env, p.required, p.optional) for p in selected]
    for prof, result in zip(selected, results):
        click.echo(f"Profile: {prof.name}")
        click.echo(format_result(result))

    click.echo(format_summary(results))
    if any(not r.ok for r in results):
        sys.exit(1)
    if strict and any(r.extra for r in results):
        sys.exit(1)


def main() -> None:
    cli()
