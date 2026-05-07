"""Tests for envsync.cli_filter."""
import argparse
from pathlib import Path

import pytest

from envsync.cli_filter import build_filter_parser, cmd_filter


@pytest.fixture()
def tmp_env(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\n"
        "DB_PORT=5432\n"
        "APP_SECRET=supersecret\n"
        "REDIS_URL=\n"
    )
    return f


def _make_args(env_file: str, **kwargs) -> argparse.Namespace:
    defaults = {
        "pattern": None,
        "prefix": None,
        "set_only": False,
        "unset_only": False,
        "show_excluded": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(env_file=env_file, **defaults)


def test_cmd_filter_returns_zero(tmp_env: Path):
    args = _make_args(str(tmp_env))
    assert cmd_filter(args) == 0


def test_cmd_filter_missing_file_returns_one(tmp_path: Path):
    args = _make_args(str(tmp_path / "missing.env"))
    assert cmd_filter(args) == 1


def test_cmd_filter_pattern_output(tmp_env: Path, capsys):
    args = _make_args(str(tmp_env), pattern=r"^DB_")
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "APP_SECRET" not in out


def test_cmd_filter_prefix_output(tmp_env: Path, capsys):
    args = _make_args(str(tmp_env), prefix="APP_")
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "APP_SECRET" in out
    assert "DB_HOST" not in out


def test_cmd_filter_set_only_excludes_empty(tmp_env: Path, capsys):
    args = _make_args(str(tmp_env), set_only=True)
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "REDIS_URL" not in out.split("Matched:")[1].split("Excluded:")[0]


def test_cmd_filter_show_excluded_lists_keys(tmp_env: Path, capsys):
    args = _make_args(str(tmp_env), pattern=r"^DB_", show_excluded=True)
    cmd_filter(args)
    out = capsys.readouterr().out
    assert "Excluded:" in out
    assert "APP_SECRET" in out


def test_cmd_filter_mutually_exclusive_flags_returns_one(tmp_env: Path):
    args = _make_args(str(tmp_env), set_only=True, unset_only=True)
    assert cmd_filter(args) == 1


def test_build_filter_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_filter_parser(sub)
    parsed = root.parse_args(["filter", "some.env", "--prefix", "DB_"])
    assert parsed.prefix == "DB_"
