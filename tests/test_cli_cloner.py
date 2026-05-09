"""Tests for envsync.cli_cloner."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envsync.cli_cloner import build_clone_parser, cmd_clone


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_env(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text("DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc123\n")
    return p


def _make_args(src, output=None, remap=None, override=None, sort=False):
    ns = argparse.Namespace(
        src=str(src),
        output=str(output) if output else None,
        remap=remap or [],
        override=override or [],
        sort=sort,
    )
    return ns


# ---------------------------------------------------------------------------
# Return codes
# ---------------------------------------------------------------------------

def test_cmd_clone_returns_zero_for_valid_file(tmp_env):
    assert cmd_clone(_make_args(tmp_env)) == 0


def test_cmd_clone_missing_file_returns_one(tmp_path):
    missing = tmp_path / "ghost.env"
    assert cmd_clone(_make_args(missing)) == 1


def test_cmd_clone_bad_remap_returns_one(tmp_env):
    assert cmd_clone(_make_args(tmp_env, remap=["NOEQUALSSIGN"])) == 1


def test_cmd_clone_bad_override_returns_one(tmp_env):
    assert cmd_clone(_make_args(tmp_env, override=["NOEQUALSSIGN"])) == 1


# ---------------------------------------------------------------------------
# Output written to file
# ---------------------------------------------------------------------------

def test_cmd_clone_writes_output_file(tmp_env, tmp_path):
    out = tmp_path / "cloned.env"
    cmd_clone(_make_args(tmp_env, output=out))
    assert out.exists()
    assert "DB_HOST" in out.read_text()


def test_cmd_clone_remap_in_output(tmp_env, tmp_path):
    out = tmp_path / "cloned.env"
    cmd_clone(_make_args(tmp_env, output=out, remap=["DB_HOST=DATABASE_HOST"]))
    content = out.read_text()
    assert "DATABASE_HOST" in content
    assert "DB_HOST" not in content


def test_cmd_clone_override_in_output(tmp_env, tmp_path):
    out = tmp_path / "cloned.env"
    cmd_clone(_make_args(tmp_env, output=out, override=["DB_PORT=9999"]))
    content = out.read_text()
    assert "9999" in content


# ---------------------------------------------------------------------------
# Parser registration
# ---------------------------------------------------------------------------

def test_build_clone_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_clone_parser(sub)
    args = root.parse_args(["clone", "some.env"])
    assert args.src == "some.env"
