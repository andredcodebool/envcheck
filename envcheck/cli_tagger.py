"""CLI commands for tagging environment variables."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from envcheck.loader import LoadError, load_from_env, load_from_file
from envcheck.tagger import all_tags, filter_by_tag, format_tag_report, tag_env, tags_from_dict


@click.group("tag", help="Tag env keys and query by tag.")
def tag_group() -> None:  # pragma: no cover
    pass


def _load_tag_map(tags_file: str) -> dict:
    path = Path(tags_file)
    if not path.exists():
        click.echo(f"error: tags file not found: {tags_file}", err=True)
        sys.exit(1)
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        click.echo(f"error: invalid JSON in tags file: {exc}", err=True)
        sys.exit(1)
    return tags_from_dict(raw)


@tag_group.command("file")
@click.argument("env_file")
@click.argument("tags_file")
@click.option("--filter", "filter_tag", default=None, help="Show only keys with this tag.")
def file_cmd(env_file: str, tags_file: str, filter_tag: str | None) -> None:
    """Tag keys in ENV_FILE using TAGS_FILE (JSON mapping key -> [tags])."""
    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)

    tag_map = _load_tag_map(tags_file)
    report = tag_env(env, tag_map)

    if filter_tag:
        keys = filter_by_tag(report, filter_tag)
        if keys:
            click.echo(f"Keys tagged '{filter_tag}':")
            for k in keys:
                click.echo(f"  {k}")
        else:
            click.echo(f"No keys found with tag '{filter_tag}'.")
    else:
        click.echo(format_tag_report(report))


@tag_group.command("env")
@click.argument("tags_file")
@click.option("--filter", "filter_tag", default=None, help="Show only keys with this tag.")
def env_cmd(tags_file: str, filter_tag: str | None) -> None:
    """Tag keys from the current process environment using TAGS_FILE."""
    env = load_from_env()
    tag_map = _load_tag_map(tags_file)
    report = tag_env(env, tag_map)

    if filter_tag:
        keys = filter_by_tag(report, filter_tag)
        click.echo(f"Keys tagged '{filter_tag}': " + (str(keys) if keys else "(none)"))
    else:
        click.echo(format_tag_report(report))


@tag_group.command("list-tags")
@click.argument("env_file")
@click.argument("tags_file")
def list_tags_cmd(env_file: str, tags_file: str) -> None:
    """List all distinct tags used in TAGS_FILE for keys present in ENV_FILE."""
    try:
        env = load_from_file(env_file)
    except LoadError as exc:
        click.echo(f"error: {exc}", err=True)
        sys.exit(1)

    tag_map = _load_tag_map(tags_file)
    report = tag_env(env, tag_map)
    tags = sorted(all_tags(report))
    if tags:
        click.echo("Available tags: " + ", ".join(tags))
    else:
        click.echo("No tags found.")
