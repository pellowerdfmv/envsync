"""Tests for envsync.cli_tagger."""
import argparse
import json
from pathlib import Path

import pytest

from envsync.cli_tagger import build_tag_parser, cmd_tag


@pytest.fixture()
def tmp_env(tmp_path: Path):
    f = tmp_path / ".env"
    f.write_text("API_KEY=abc123\nDB_URL=postgres://localhost\nDEBUG=true\n")
    return f


@pytest.fixture()
def tag_file(tmp_path: Path):
    data = {"API_KEY": ["secret", "required"], "DB_URL": ["required"], "DEBUG": ["optional"]}
    f = tmp_path / "tags.json"
    f.write_text(json.dumps(data))
    return f


def _make_args(env_file, tag_file, strict=False, filter_tag=None):
    ns = argparse.Namespace(
        env_file=str(env_file),
        tag_file=str(tag_file),
        strict=strict,
        filter_tag=filter_tag,
    )
    return ns


def test_cmd_tag_returns_zero(tmp_env, tag_file):
    assert cmd_tag(_make_args(tmp_env, tag_file)) == 0


def test_cmd_tag_missing_env_returns_one(tmp_path, tag_file):
    missing = tmp_path / "no.env"
    assert cmd_tag(_make_args(missing, tag_file)) == 1


def test_cmd_tag_missing_tag_file_returns_one(tmp_env, tmp_path):
    missing = tmp_path / "no_tags.json"
    assert cmd_tag(_make_args(tmp_env, missing)) == 1


def test_cmd_tag_output_contains_key(tmp_env, tag_file, capsys):
    cmd_tag(_make_args(tmp_env, tag_file))
    out = capsys.readouterr().out
    assert "API_KEY" in out


def test_cmd_tag_filter_shows_only_matching_keys(tmp_env, tag_file, capsys):
    cmd_tag(_make_args(tmp_env, tag_file, filter_tag="required"))
    out = capsys.readouterr().out
    assert "API_KEY" in out
    assert "DB_URL" in out
    assert "DEBUG" not in out


def test_cmd_tag_filter_no_match_message(tmp_env, tag_file, capsys):
    cmd_tag(_make_args(tmp_env, tag_file, filter_tag="internal"))
    out = capsys.readouterr().out
    assert "No keys" in out


def test_build_tag_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    build_tag_parser(subs)
    args = root.parse_args(["tag", "my.env", "--tag-file", "tags.json"])
    assert args.env_file == "my.env"
    assert args.tag_file == "tags.json"
    assert args.strict is False


def test_build_tag_parser_strict_flag():
    root = argparse.ArgumentParser()
    subs = root.add_subparsers()
    build_tag_parser(subs)
    args = root.parse_args(["tag", "my.env", "--tag-file", "tags.json", "--strict"])
    assert args.strict is True
