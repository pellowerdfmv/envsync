"""Tests for envsync.cli_pinner."""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from envsync.cli_pinner import build_pin_parser, cmd_pin


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Return a factory that writes a .env file and returns its Path."""

    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(content)
        return p

    return _write


def _make_args(
    env_file: str,
    assignments: list,
    allow_new: bool = False,
    dry_run: bool = False,
) -> argparse.Namespace:
    return argparse.Namespace(
        env_file=env_file,
        assignments=assignments,
        allow_new=allow_new,
        dry_run=dry_run,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_cmd_pin_returns_zero_for_valid_file(tmp_env):
    path = tmp_env("HOST=localhost\nPORT=5432\n")
    args = _make_args(str(path), ["HOST=prod.db"])
    assert cmd_pin(args) == 0


def test_cmd_pin_missing_file_returns_one(tmp_path):
    args = _make_args(str(tmp_path / "missing.env"), ["KEY=val"])
    assert cmd_pin(args) == 1


def test_cmd_pin_writes_updated_value(tmp_env):
    path = tmp_env("HOST=localhost\nPORT=5432\n")
    args = _make_args(str(path), ["HOST=prod.db"])
    cmd_pin(args)
    content = path.read_text()
    assert "HOST=prod.db" in content


def test_cmd_pin_dry_run_does_not_write(tmp_env):
    path = tmp_env("HOST=localhost\n")
    original = path.read_text()
    args = _make_args(str(path), ["HOST=changed"], dry_run=True)
    cmd_pin(args)
    assert path.read_text() == original


def test_cmd_pin_allow_new_adds_key(tmp_env):
    path = tmp_env("EXISTING=yes\n")
    args = _make_args(str(path), ["NEW_KEY=hello"], allow_new=True)
    cmd_pin(args)
    assert "NEW_KEY=hello" in path.read_text()


def test_build_pin_parser_registers_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    build_pin_parser(sub)
    ns = parser.parse_args(["pin", "myfile.env", "KEY=val"])
    assert ns.env_file == "myfile.env"
    assert ns.assignments == ["KEY=val"]
