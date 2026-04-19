"""CLI commands for transforming env files."""
from __future__ import annotations

import sys

import click

from envcheck.loader import LoadError, load_from_file, load_from_string
from envcheck.transformer import filter_keys, merge_envs, prefix_keys, strip_prefix


@click.group("transform", help="Transform env variable maps.")
def transform_group() -> None:  # pragma: no cover
    pass


@transform_group.command("prefix")
@click.argument("envfile", type=click.Path(exists=True))
@click.argument("prefix")
@click.option("--strip", is_flag=True, help="Strip prefix instead of adding it.")
def prefix_cmd(envfile: str, prefix: str, strip: bool) -> None:
    """Add or strip PREFIX from all keys in ENVFILE."""
    try:
        env = load_from_file(envfile)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    result = strip_prefix(env, prefix) if strip else prefix_keys(env, prefix)
    for k, v in result.items():
        click.echo(f"{k}={v}")


@transform_group.command("filter")
@click.argument("envfile", type=click.Path(exists=True))
@click.option("--include", multiple=True, metavar="KEY", help="Keys to keep.")
@click.option("--exclude", multiple=True, metavar="KEY", help="Keys to drop.")
def filter_cmd(envfile: str, include: tuple, exclude: tuple) -> None:
    """Filter keys in ENVFILE by include/exclude lists."""
    try:
        env = load_from_file(envfile)
    except LoadError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    result = filter_keys(
        env,
        include=list(include) or None,
        exclude=list(exclude) or None,
    )
    for k, v in result.items():
        click.echo(f"{k}={v}")


@transform_group.command("merge")
@click.argument("envfiles", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--strategy",
    default="last",
    show_default=True,
    type=click.Choice(["first", "last"]),
    help="Merge strategy when keys collide.",
)
def merge_cmd(envfiles: tuple, strategy: str) -> None:
    """Merge multiple ENVFILES into one, writing to stdout."""
    maps = []
    for path in envfiles:
        try:
            maps.append(load_from_file(path))
        except LoadError as exc:
            click.echo(f"Error loading {path}: {exc}", err=True)
            sys.exit(1)
    result = merge_envs(*maps, strategy=strategy)
    for k, v in result.items():
        click.echo(f"{k}={v}")
