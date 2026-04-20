"""CLI commands for value-level validation of env files."""
from __future__ import annotations

import json
import sys
from typing import Optional

import click

from envcheck.loader import load_from_file, load_from_env, LoadError
from envcheck.validator import validate, format_validation


@click.group("validate")
def validate_group() -> None:
    """Validate env variable values against rules."""


@validate_group.command("file")
@click.argument("env_file", type=click.Path(exists=True))
@click.option(
    "--rules",
    "rules_file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file mapping key -> list of rule names.",
)
@click.option("--quiet", is_flag=True, default=False, help="Suppress output on success.")
def file_cmd(env_file: str, rules_file: str, quiet: bool) -> None:
    """Validate values in ENV_FILE using RULES_FILE."""
    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"error loading env file: {exc}", err=True)
        sys.exit(2)

    rules = _load_rules(rules_file)
    report = validate(env, rules)
    _emit(report, quiet)


@validate_group.command("env")
@click.option(
    "--rules",
    "rules_file",
    required=True,
    type=click.Path(exists=True),
    help="JSON file mapping key -> list of rule names.",
)
@click.option("--quiet", is_flag=True, default=False, help="Suppress output on success.")
def env_cmd(rules_file: str, quiet: bool) -> None:
    """Validate the current process environment using RULES_FILE."""
    env = load_from_env()
    rules = _load_rules(rules_file)
    report = validate(env, rules)
    _emit(report, quiet)


def _load_rules(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        click.echo(f"error loading rules file: {exc}", err=True)
        sys.exit(2)


def _emit(report, quiet: bool) -> None:
    if report.ok:
        if not quiet:
            click.echo(format_validation(report))
        sys.exit(0)
    else:
        click.echo(format_validation(report))
        sys.exit(1)
