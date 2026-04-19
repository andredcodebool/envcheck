"""CLI commands for linting env files."""
from __future__ import annotations

import sys
import click

from envcheck.loader import load_from_file, load_from_env, LoadError
from envcheck.linter import lint_env, format_lint


@click.group("lint")
def lint_group() -> None:
    """Lint env variable keys and values for common issues."""


@lint_group.command("file")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too")
def file_cmd(path: str, no_color: bool, strict: bool) -> None:
    """Lint an env file at PATH."""
    try:
        env = load_from_file(path)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(2)

    report = lint_env(env)
    click.echo(format_lint(report, color=not no_color))

    if not report.ok:
        has_errors = any(i.code.startswith("E") for i in report.issues)
        has_warnings = any(i.code.startswith("W") for i in report.issues)
        if has_errors or (strict and has_warnings):
            sys.exit(1)


@lint_group.command("env")
@click.option("--no-color", is_flag=True, default=False, help="Disable colored output")
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero on warnings too")
def env_cmd(no_color: bool, strict: bool) -> None:
    """Lint the current process environment."""
    env = load_from_env()
    report = lint_env(env)
    click.echo(format_lint(report, color=not no_color))

    if not report.ok:
        has_errors = any(i.code.startswith("E") for i in report.issues)
        has_warnings = any(i.code.startswith("W") for i in report.issues)
        if has_errors or (strict and has_warnings):
            sys.exit(1)
