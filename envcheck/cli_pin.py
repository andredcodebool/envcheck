"""CLI commands for pinning and comparing environment snapshots."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from envcheck.loader import load_from_file, load_from_env
from envcheck.pinner import (
    PinError,
    compare_pin,
    format_pin_report,
    list_pins,
    save_pin,
)

_DEFAULT_PIN_DIR = Path(".envcheck") / "pins"


@click.group("pin", help="Pin and compare environment variable snapshots.")
def pin_group() -> None:  # pragma: no cover
    pass


@pin_group.command("save")
@click.argument("name")
@click.option("-f", "--file", "env_file", default=None, help=".env file to pin (default: live env).")
@click.option("--pin-dir", default=str(_DEFAULT_PIN_DIR), show_default=True)
def save_cmd(name: str, env_file: Optional[str], pin_dir: str) -> None:
    """Save a named pin of the current environment or a file."""
    try:
        env = load_from_file(Path(env_file)) if env_file else load_from_env()
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error loading env: {exc}", err=True)
        sys.exit(1)

    path = save_pin(env, name, Path(pin_dir))
    click.echo(f"Pinned '{name}' → {path}")


@pin_group.command("list")
@click.option("--pin-dir", default=str(_DEFAULT_PIN_DIR), show_default=True)
def list_cmd(pin_dir: str) -> None:
    """List all saved pins."""
    names = list_pins(Path(pin_dir))
    if not names:
        click.echo("No pins saved yet.")
        return
    for name in names:
        click.echo(f"  {name}")


@pin_group.command("compare")
@click.argument("name")
@click.option("-f", "--file", "env_file", default=None, help=".env file to compare (default: live env).")
@click.option("--pin-dir", default=str(_DEFAULT_PIN_DIR), show_default=True)
def compare_cmd(name: str, env_file: Optional[str], pin_dir: str) -> None:
    """Compare current environment (or file) against a saved pin."""
    try:
        env = load_from_file(Path(env_file)) if env_file else load_from_env()
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error loading env: {exc}", err=True)
        sys.exit(1)

    try:
        report = compare_pin(env, name, Path(pin_dir))
    except PinError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)

    click.echo(format_pin_report(report))
    if not report.clean:
        sys.exit(1)
