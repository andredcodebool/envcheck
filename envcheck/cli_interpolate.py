"""CLI commands for variable interpolation."""
from __future__ import annotations

import sys

import click

from envcheck.interpolator import InterpolationError, interpolate_all, missing_refs
from envcheck.loader import LoadError, load_from_file, load_from_env


@click.group("interpolate")
def interpolate_group() -> None:
    """Interpolate ${VAR} references inside env files."""


@interpolate_group.command("resolve")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Error on unresolved references.")
@click.option("--show-missing", is_flag=True, help="List unresolved references and exit.")
def resolve_cmd(env_file: str, strict: bool, show_missing: bool) -> None:
    """Resolve ${VAR} references in ENV_FILE and print the result."""
    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if show_missing:
        found: list[str] = []
        for key, val in env.items():
            found.extend(missing_refs(val, env))
        if found:
            click.echo("Unresolved references:")
            for ref in sorted(set(found)):
                click.echo(f"  ${{{ref}}}")
            sys.exit(1)
        click.echo("No unresolved references.")
        return

    try:
        resolved = interpolate_all(env, strict=strict)
    except InterpolationError as exc:
        click.echo(f"Interpolation error: {exc}", err=True)
        sys.exit(1)

    for key, val in resolved.items():
        click.echo(f"{key}={val}")


@interpolate_group.command("check-refs")
@click.argument("env_file", type=click.Path(exists=True))
def check_refs_cmd(env_file: str) -> None:
    """Report any unresolved ${VAR} references in ENV_FILE."""
    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    issues: dict[str, list[str]] = {}
    for key, val in env.items():
        missing = missing_refs(val, env)
        if missing:
            issues[key] = missing

    if not issues:
        click.echo("All references resolved.")
        return

    click.echo("Unresolved references found:")
    for key, refs in issues.items():
        click.echo(f"  {key}: " + ", ".join(f"${{{r}}}" for r in refs))
    sys.exit(1)
