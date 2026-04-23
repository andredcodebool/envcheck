"""CLI commands for patching env files."""
from __future__ import annotations

import sys
from typing import List, Optional

import click

from envcheck.loader import load_from_file, load_from_env
from envcheck.patcher import apply_patch, format_patch
from envcheck.parser import parse_env_string


def _parse_set(pairs: tuple[str, ...]) -> dict[str, str]:
    result: dict[str, str] = {}
    for pair in pairs:
        if "=" not in pair:
            raise click.BadParameter(f"Expected KEY=VALUE, got: {pair!r}")
        k, v = pair.split("=", 1)
        result[k.strip()] = v
    return result


@click.group("patch")
def patch_group() -> None:
    """Patch (add/update/remove) keys in env files."""


@patch_group.command("file")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--set", "set_pairs", multiple=True, metavar="KEY=VALUE",
              help="Set a key to a value (repeatable).")
@click.option("--remove", "remove_keys", multiple=True, metavar="KEY",
              help="Remove a key (repeatable).")
@click.option("--output", "-o", type=click.Path(), default=None,
              help="Write patched env to this file (default: stdout).")
@click.option("--quiet", "-q", is_flag=True, help="Suppress patch summary.")
def file_cmd(
    env_file: str,
    set_pairs: tuple[str, ...],
    remove_keys: tuple[str, ...],
    output: Optional[str],
    quiet: bool,
) -> None:
    """Patch an env file and emit the result."""
    env = load_from_file(env_file)
    set_keys = _parse_set(set_pairs)
    patched, report = apply_patch(env, set_keys=set_keys, remove_keys=list(remove_keys))

    lines = [f"{k}={v}" for k, v in sorted(patched.items())]
    content = "\n".join(lines) + ("\n" if lines else "")

    if output:
        with open(output, "w") as fh:
            fh.write(content)
    else:
        click.echo(content, nl=False)

    if not quiet:
        click.echo(format_patch(report), err=True)


@patch_group.command("env")
@click.option("--set", "set_pairs", multiple=True, metavar="KEY=VALUE")
@click.option("--remove", "remove_keys", multiple=True, metavar="KEY")
@click.option("--quiet", "-q", is_flag=True)
def env_cmd(
    set_pairs: tuple[str, ...],
    remove_keys: tuple[str, ...],
    quiet: bool,
) -> None:
    """Patch the current process environment and print the result."""
    env = load_from_env()
    set_keys = _parse_set(set_pairs)
    patched, report = apply_patch(env, set_keys=set_keys, remove_keys=list(remove_keys))

    for k, v in sorted(patched.items()):
        click.echo(f"{k}={v}")

    if not quiet:
        click.echo(format_patch(report), err=True)
