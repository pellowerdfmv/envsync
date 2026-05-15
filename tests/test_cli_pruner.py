"""Tests for envsync.cli_pruner."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envsync.cli_pruner import build_prune_parser, cmd_prune


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\nAPP=myapp\n")
    return p


def _make_args(
    env_file: Path,
    keys: list[str] | None = None,
    patterns: list[str] | None = None,
    quiet: bool = False,
) -> argparse.Namespace:
    return argparse.Namespace(
        env_file=env_file,
        keys=keys or [],
        patterns=patterns or [],
        quiet=quiet,
    )


# ---------------------------------------------------------------------------
# cmd_prune return codes
# ---------------------------------------------------------------------------

def test_cmd_prune_returns_zero_for_valid_file(tmp_env):
    args = _make_args(tmp_env, keys=["SECRET"])
    assert cmd_prune(args) == 0


def test_cmd_prune_missing_file_returns_one(tmp_path):
    args = _make_args(tmp_path / "missing.env")
    assert cmd_prune(args) == 1


def test_cmd_prune_no_filters_returns_zero(tmp_env):
    args = _make_args(tmp_env)
    assert cmd_prune(args) == 0


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

def test_cmd_prune_quiet_suppresses_output(tmp_env, capsys):
    args = _make_args(tmp_env, keys=["SECRET"], quiet=True)
    cmd_prune(args)
    captured = capsys.readouterr()
    assert captured.out == ""


def test_cmd_prune_prints_summary(tmp_env, capsys):
    args = _make_args(tmp_env, keys=["SECRET"])
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "SECRET" in out


def test_cmd_prune_pattern_output(tmp_env, capsys):
    args = _make_args(tmp_env, patterns=[r"DB_.*"])
    cmd_prune(args)
    out = capsys.readouterr().out
    assert "DB_HOST" in out or "DB_PORT" in out


# ---------------------------------------------------------------------------
# build_prune_parser smoke test
# ---------------------------------------------------------------------------

def test_build_prune_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers(dest="command")
    p = build_prune_parser(sub)
    assert p is not None
