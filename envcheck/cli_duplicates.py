"""CLI commands for duplicate-key detection."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import click

from .duplicates import scan, format_report
from .loader import load_from_file, load_from_env


@click.group("duplicates", help="Detect duplicate environment variable keys.")
def duplicates_group() -> None:  # pragma: no cover
    pass


@duplicates_group.command("file")
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--no-color", is_flag=True, default=False, help="Disable ANSI colours.")
def file_cmd(files: tuple[str, ...], no_color: bool) -> None:
    """Scan one or more .env FILES for duplicate keys.

    When a single file is given, intra-source duplicates are reported.
    When multiple files are given, both intra and inter-source duplicates
    are reported.
    """
    paths: List[Path] = [Path(f) for f in files]
    color = not no_color

    # Intra-source: read raw lines from each file
    all_lines: List[str] = []
    envs = []
    for path in paths:
        raw = path.read_text(encoding="utf-8").splitlines()
        all_lines.extend(raw)
        envs.append(load_from_file(path))

    if len(paths) == 1:
        report = scan(lines=all_lines)
    else:
        report = scan(lines=all_lines, envs=envs)

    click.echo(format_report(report, color=color))
    sys.exit(1 if report.has_duplicates else 0)


@duplicates_group.command("env")
@click.option(
    "--against",
    "against_files",
    multiple=True,
    type=click.Path(exists=True),
    help="Additional .env file(s) to compare against the live environment.",
)
@click.option("--no-color", is_flag=True, default=False, help="Disable ANSI colours.")
def env_cmd(against_files: tuple[str, ...], no_color: bool) -> None:
    """Check the live environment for inter-source duplicate keys.

    Optionally supply --against files to include additional sources.
    """
    color = not no_color
    live = load_from_env()
    envs = [live]
    for f in against_files:
        envs.append(load_from_file(Path(f)))

    report = scan(envs=envs)
    click.echo(format_report(report, color=color))
    sys.exit(1 if report.has_duplicates else 0)
