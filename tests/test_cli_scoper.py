"""Tests for envsync.cli_scoper."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envsync.cli_scoper import build_scope_parser, cmd_scope


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


@pytest.fixture()
def tmp_env(tmp_path):
    return _write(
        tmp_path / ".env",
        "DB_HOST=localhost\nDB_PORT=5432\nAPP_NAME=envsync\n",
    )


def _make_args(env_file, keys, scope="default", show_excluded=False):
    ns = argparse.Namespace(
        env_file=str(env_file),
        keys=keys,
        scope=scope,
        show_excluded=show_excluded,
    )
    return ns


# ---------------------------------------------------------------------------
# cmd_scope
# ---------------------------------------------------------------------------

def test_cmd_scope_returns_zero_for_valid_file(tmp_env):
    args = _make_args(tmp_env, ["DB_HOST", "DB_PORT"])
    assert cmd_scope(args) == 0


def test_cmd_scope_missing_file_returns_one(tmp_path):
    args = _make_args(tmp_path / "missing.env", ["DB_HOST"])
    assert cmd_scope(args) == 1


def test_cmd_scope_output_contains_included_key(tmp_env, capsys):
    args = _make_args(tmp_env, ["DB_HOST"])
    cmd_scope(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out


def test_cmd_scope_excluded_key_absent_by_default(tmp_env, capsys):
    args = _make_args(tmp_env, ["DB_HOST"])
    cmd_scope(args)
    out = capsys.readouterr().out
    assert "APP_NAME" not in out


def test_cmd_scope_show_excluded_prints_excluded_keys(tmp_env, capsys):
    args = _make_args(tmp_env, ["DB_HOST"], show_excluded=True)
    cmd_scope(args)
    out = capsys.readouterr().out
    assert "APP_NAME" in out


def test_cmd_scope_summary_in_output(tmp_env, capsys):
    args = _make_args(tmp_env, ["DB_HOST", "DB_PORT"], scope="db")
    cmd_scope(args)
    out = capsys.readouterr().out
    assert "db" in out


# ---------------------------------------------------------------------------
# build_scope_parser
# ---------------------------------------------------------------------------

def test_build_scope_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_scope_parser(sub)
    args = root.parse_args(["scope", ".env", "DB_HOST", "DB_PORT"])
    assert args.keys == ["DB_HOST", "DB_PORT"]


def test_build_scope_parser_default_scope():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_scope_parser(sub)
    args = root.parse_args(["scope", ".env", "KEY"])
    assert args.scope == "default"
