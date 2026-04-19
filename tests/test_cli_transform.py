"""Tests for envcheck.cli_transform."""
import pytest
from click.testing import CliRunner

from envcheck.cli_transform import transform_group


@pytest.fixture()
def runner():
    return CliRunner()


@pytest.fixture()
def env_file(tmp_path):
    p = tmp_path / ".env"
    p.write_text("HOST=localhost\nPORT=5432\nPASSWORD=secret\n")
    return str(p)


@pytest.fixture()
def env_file2(tmp_path):
    p = tmp_path / ".env2"
    p.write_text("PORT=9999\nDEBUG=true\n")
    return str(p)


def test_prefix_adds_prefix(runner, env_file):
    result = runner.invoke(transform_group, ["prefix", env_file, "APP_"])
    assert result.exit_code == 0
    assert "APP_HOST=localhost" in result.output
    assert "APP_PORT=5432" in result.output


def test_prefix_strip_removes_prefix(runner, tmp_path, runner_):
    p = tmp_path / "prefixed.env"
    p.write_text("APP_HOST=localhost\nAPP_PORT=5432\n")
    r = CliRunner().invoke(transform_group, ["prefix", str(p), "APP_", "--strip"])
    assert r.exit_code == 0
    assert "HOST=localhost" in r.output
    assert "PORT=5432" in r.output


def test_filter_include(runner, env_file):
    result = runner.invoke(
        transform_group, ["filter", env_file, "--include", "HOST", "--include", "PORT"]
    )
    assert result.exit_code == 0
    assert "HOST=localhost" in result.output
    assert "PORT=5432" in result.output
    assert "PASSWORD" not in result.output


def test_filter_exclude(runner, env_file):
    result = runner.invoke(
        transform_group, ["filter", env_file, "--exclude", "PASSWORD"]
    )
    assert result.exit_code == 0
    assert "PASSWORD" not in result.output
    assert "HOST=localhost" in result.output


def test_merge_last_wins(runner, env_file, env_file2):
    result = runner.invoke(
        transform_group, ["merge", env_file, env_file2, "--strategy", "last"]
    )
    assert result.exit_code == 0
    assert "PORT=9999" in result.output
    assert "DEBUG=true" in result.output


def test_merge_first_wins(runner, env_file, env_file2):
    result = runner.invoke(
        transform_group, ["merge", env_file, env_file2, "--strategy", "first"]
    )
    assert result.exit_code == 0
    assert "PORT=5432" in result.output


# fixture alias used in one test above
@pytest.fixture()
def runner_():
    return CliRunner()
