"""Tests for envsync.cli_labeler."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from envsync.cli_labeler import build_label_parser, cmd_label


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


@pytest.fixture()
def tmp_env(tmp_path) -> Path:
    return _write(
        tmp_path / ".env",
        "DB_HOST=localhost\nDB_PORT=5432\nAPP_KEY=secret\nOTHER=x\n",
    )


@pytest.fixture()
def rules_file(tmp_path) -> Path:
    rules = {"database": ["DB_HOST", "DB_PORT"], "app": ["APP_KEY"]}
    p = tmp_path / "rules.json"
    p.write_text(json.dumps(rules))
    return p


def _make_args(tmp_path, env_file, rules, **kwargs) -> argparse.Namespace:
    defaults = {
        "env_file": env_file,
        "rules": rules,
        "filter_label": None,
        "show_unlabeled": False,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_cmd_label_returns_zero_for_valid_file(tmp_path, tmp_env, rules_file):
    args = _make_args(tmp_path, tmp_env, rules_file)
    assert cmd_label(args) == 0


def test_cmd_label_missing_env_returns_one(tmp_path, rules_file):
    args = _make_args(tmp_path, tmp_path / "missing.env", rules_file)
    assert cmd_label(args) == 1


def test_cmd_label_missing_rules_returns_one(tmp_path, tmp_env):
    args = _make_args(tmp_path, tmp_env, tmp_path / "missing.json")
    assert cmd_label(args) == 1


def test_cmd_label_invalid_json_returns_one(tmp_path, tmp_env):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("not valid json{{{")
    args = _make_args(tmp_path, tmp_env, bad_json)
    assert cmd_label(args) == 1


def test_cmd_label_filter_label_output(tmp_path, tmp_env, rules_file, capsys):
    args = _make_args(tmp_path, tmp_env, rules_file, filter_label="database")
    rc = cmd_label(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "DB_HOST" in out
    assert "DB_PORT" in out
    assert "APP_KEY" not in out


def test_cmd_label_show_unlabeled(tmp_path, tmp_env, rules_file, capsys):
    args = _make_args(tmp_path, tmp_env, rules_file, show_unlabeled=True)
    rc = cmd_label(args)
    assert rc == 0
    out = capsys.readouterr().out
    assert "OTHER" in out


def test_build_label_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    p = build_label_parser(sub)
    assert p is not None
