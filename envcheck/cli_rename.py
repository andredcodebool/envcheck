"""CLI commands for renaming environment variable keys using rule sets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from .loader import load_from_file, load_from_env, LoadError
from .renamer import apply_rules, rules_from_dict, RenameReport


def _load_rules_file(rules_path: str) -> list:
    """Load rename rules from a JSON file.

    Expected format::

        [
          {"from": "OLD_KEY", "to": "NEW_KEY"},
          {"prefix": "OLD_", "replace_with": "NEW_"}
        ]
    """
    path = Path(rules_path)
    if not path.exists():
        raise click.ClickException(f"Rules file not found: {rules_path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise click.ClickException(f"Invalid JSON in rules file: {exc}") from exc
    if not isinstance(data, list):
        raise click.ClickException("Rules file must contain a JSON array of rule objects.")
    return data


def _emit_report(report: RenameReport, output: str | None, dry_run: bool) -> None:
    """Print the renamed env vars and a summary of applied rules."""
    click.echo(f"Renamed {len(report.renamed)} key(s), {len(report.unchanged)} unchanged.")
    if report.renamed:
        click.echo("\nRenamed:")
        for old, new in report.renamed:
            click.echo(f"  {old}  ->  {new}")

    if dry_run:
        click.echo("\n[dry-run] No output written.")
        return

    lines = "".join(f"{k}={v}\n" for k, v in sorted(report.result.items()))
    if output:
        Path(output).write_text(lines)
        click.echo(f"\nWrote {len(report.result)} variable(s) to {output}")
    else:
        click.echo("\nResult:")
        click.echo(lines, nl=False)


@click.group(name="rename")
def rename_group() -> None:
    """Rename environment variable keys using rule sets."""


@rename_group.command(name="file")
@click.argument("env_file")
@click.argument("rules_file")
@click.option("--output", "-o", default=None, help="Write result to this file instead of stdout.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would change without writing output.")
def file_cmd(env_file: str, rules_file: str, output: str | None, dry_run: bool) -> None:
    """Rename keys in ENV_FILE according to rules in RULES_FILE."""
    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        raise click.ClickException(str(exc)) from exc

    raw_rules = _load_rules_file(rules_file)
    try:
        rules = rules_from_dict(raw_rules)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(f"Invalid rule definition: {exc}") from exc

    report = apply_rules(env, rules)
    _emit_report(report, output, dry_run)
    sys.exit(0)


@rename_group.command(name="env")
@click.argument("rules_file")
@click.option("--output", "-o", default=None, help="Write result to this file instead of stdout.")
@click.option("--dry-run", is_flag=True, default=False, help="Show what would change without writing output.")
def env_cmd(rules_file: str, output: str | None, dry_run: bool) -> None:
    """Rename keys from the current process environment according to rules in RULES_FILE."""
    env = load_from_env()

    raw_rules = _load_rules_file(rules_file)
    try:
        rules = rules_from_dict(raw_rules)
    except (KeyError, ValueError) as exc:
        raise click.ClickException(f"Invalid rule definition: {exc}") from exc

    report = apply_rules(env, rules)
    _emit_report(report, output, dry_run)
    sys.exit(0)
