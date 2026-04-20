"""CLI commands for health-score reporting."""
from __future__ import annotations

import sys

import click

from envcheck.checker import check_env
from envcheck.config import get_profiles, load_config
from envcheck.linter import lint_env
from envcheck.loader import load_from_env, load_from_file
from envcheck.scorer import format_score, score_env
from envcheck.validator import validate_env


@click.group("score")
def score_group() -> None:
    """Compute a composite health score for an env set."""


@score_group.command("file")
@click.argument("env_file", type=click.Path(exists=True))
@click.option("--profile", "profile_name", default=None, help="Profile to validate against.")
@click.option("--config", "config_path", default=None, type=click.Path(), help="Config file.")
@click.option("--rules", "rules_path", default=None, type=click.Path(exists=True), help="Validation rules TOML.")
@click.option("--json", "as_json", is_flag=True, default=False)
def file_cmd(
    env_file: str,
    profile_name: str | None,
    config_path: str | None,
    rules_path: str | None,
    as_json: bool,
) -> None:
    """Score an env file."""
    env = load_from_file(env_file)
    _run_score(env, profile_name, config_path, rules_path, as_json)


@score_group.command("env")
@click.option("--profile", "profile_name", default=None)
@click.option("--config", "config_path", default=None, type=click.Path())
@click.option("--rules", "rules_path", default=None, type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, default=False)
def env_cmd(
    profile_name: str | None,
    config_path: str | None,
    rules_path: str | None,
    as_json: bool,
) -> None:
    """Score the current process environment."""
    env = load_from_env()
    _run_score(env, profile_name, config_path, rules_path, as_json)


def _run_score(
    env: dict[str, str],
    profile_name: str | None,
    config_path: str | None,
    rules_path: str | None,
    as_json: bool,
) -> None:
    check_result = None
    lint_result = lint_env(env)
    val_result = None

    if profile_name:
        try:
            cfg = load_config(config_path)
            profiles = get_profiles(cfg)
            profile = profiles.get(profile_name)
            if profile is None:
                click.echo(f"Profile '{profile_name}' not found.", err=True)
                sys.exit(2)
            check_result = check_env(env, profile.required)
        except Exception as exc:  # noqa: BLE001
            click.echo(f"Config error: {exc}", err=True)
            sys.exit(2)

    if rules_path:
        import tomllib  # type: ignore[import]
        with open(rules_path, "rb") as fh:
            rules_data = tomllib.load(fh)
        val_result = validate_env(env, rules_data.get("rules", {}))

    report = score_env(check=check_result, lint=lint_result, validation=val_result)

    if as_json:
        import json
        click.echo(json.dumps({
            "score": report.score,
            "total": report.total,
            "grade": report.grade,
            "deductions": [list(d) for d in report.deductions],
        }))
    else:
        click.echo(format_score(report))

    if report.grade in ("D", "F"):
        sys.exit(1)
