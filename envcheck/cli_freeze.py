"""CLI commands for the freeze/thaw feature."""
from __future__ import annotations

import os
from pathlib import Path

import click

from envcheck.freezer import FreezeError, freeze, list_freezes, thaw, write_env_file
from envcheck.loader import load_from_env, load_from_file

_DEFAULT_DIR = Path(".envcheck_freezes")


@click.group("freeze")
def freeze_group() -> None:
    """Freeze and thaw environment variable snapshots."""


@freeze_group.command("save")
@click.option("--name", required=True, help="Label for this freeze.")
@click.option("--file", "env_file", default=None, help="Source .env file (default: live env).")
@click.option("--dir", "dest_dir", default=str(_DEFAULT_DIR), show_default=True)
def save_cmd(name: str, env_file: str | None, dest_dir: str) -> None:
    """Freeze an environment to a named JSON file."""
    if env_file:
        env = load_from_file(Path(env_file))
    else:
        env = load_from_env()
    out = freeze(env, name, Path(dest_dir))
    click.echo(f"Frozen {len(env)} keys to {out}")


@freeze_group.command("list")
@click.option("--dir", "src_dir", default=str(_DEFAULT_DIR), show_default=True)
def list_cmd(src_dir: str) -> None:
    """List available freeze files."""
    files = list_freezes(Path(src_dir))
    if not files:
        click.echo("No freeze files found.")
        return
    for f in files:
        click.echo(f.name)


@freeze_group.command("thaw")
@click.argument("name")
@click.option("--dir", "src_dir", default=str(_DEFAULT_DIR), show_default=True)
@click.option("--output", default=None, help="Write result to a .env file.")
def thaw_cmd(name: str, src_dir: str, output: str | None) -> None:
    """Restore a freeze file and optionally write it as a .env file."""
    src = Path(src_dir) / f"{name}.freeze.json"
    try:
        record = thaw(src)
    except FreezeError as exc:
        raise click.ClickException(str(exc))

    if output:
        write_env_file(record, Path(output))
        click.echo(f"Wrote {len(record.env)} keys to {output}")
    else:
        for k, v in sorted(record.env.items()):
            click.echo(f"{k}={v}")
