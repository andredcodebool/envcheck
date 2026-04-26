"""CLI commands for diffing two environment files or sources."""

from __future__ import annotations

import click

from .differ import diff_envs, format_diff, has_diff
from .loader import LoadError, load_from_env, load_from_file, load_from_string


@click.group("diff", help="Compare two environment sources and show differences.")
def diff_group() -> None:  # pragma: no cover
    pass


@diff_group.command("files", help="Diff two .env files.")
@click.argument("left", type=click.Path(exists=True, dir_okay=False))
@click.argument("right", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--only-changed",
    is_flag=True,
    default=False,
    help="Suppress unchanged keys from output.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 if differences are found.",
)
def files_cmd(
    left: str,
    right: str,
    only_changed: bool,
    exit_code: bool,
) -> None:
    """Load two env files and display a diff."""
    try:
        left_env = load_from_file(left)
        right_env = load_from_file(right)
    except LoadError as exc:
        raise click.ClickException(str(exc)) from exc

    result = diff_envs(left_env, right_env, label_a=left, label_b=right)
    output = format_diff(result, only_changed=only_changed)
    click.echo(output)

    if exit_code and has_diff(result):
        raise SystemExit(1)


@diff_group.command("env-vs-file", help="Diff the current process environment against a .env file.")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--only-changed",
    is_flag=True,
    default=False,
    help="Suppress unchanged keys from output.",
)
@click.option(
    "--exit-code",
    is_flag=True,
    default=False,
    help="Exit with code 1 if differences are found.",
)
def env_vs_file_cmd(
    file: str,
    only_changed: bool,
    exit_code: bool,
) -> None:
    """Compare the live process environment to a reference .env file."""
    try:
        file_env = load_from_file(file)
    except LoadError as exc:
        raise click.ClickException(str(exc)) from exc

    live_env = load_from_env()
    result = diff_envs(live_env, file_env, label_a="<live env>", label_b=file)
    output = format_diff(result, only_changed=only_changed)
    click.echo(output)

    if exit_code and has_diff(result):
        raise SystemExit(1)


@diff_group.command("strings", help="Diff two inline KEY=VALUE strings (semicolon-separated).")
@click.argument("left")
@click.argument("right")
@click.option(
    "--only-changed",
    is_flag=True,
    default=False,
    help="Suppress unchanged keys from output.",
)
def strings_cmd(left: str, right: str, only_changed: bool) -> None:
    """Parse two semicolon-separated env strings and diff them.

    Example::

        envcheck diff strings "A=1;B=2" "A=1;B=3;C=4"
    """
    # Accept both semicolon and newline as separators for convenience.
    left_env = load_from_string(left.replace(";", "\n"))
    right_env = load_from_string(right.replace(";", "\n"))

    result = diff_envs(left_env, right_env, label_a="left", label_b="right")
    click.echo(format_diff(result, only_changed=only_changed))
