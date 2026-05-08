"""Tests for envsync.cli_caster."""
import argparse
import json
import pytest

from envsync.cli_caster import build_cast_parser, cmd_cast


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path / ".env"


def _make_args(env_file, schema="{}", output="summary"):
    ns = argparse.Namespace()
    ns.env_file = str(env_file)
    ns.schema = schema
    ns.output = output
    return ns


def test_cmd_cast_returns_zero_for_clean_file(tmp_env):
    tmp_env.write_text("PORT=8080\nDEBUG=true\n")
    args = _make_args(tmp_env, schema='{"PORT":"int","DEBUG":"bool"}')
    assert cmd_cast(args) == 0


def test_cmd_cast_missing_file_returns_one(tmp_env):
    args = _make_args(tmp_env)  # file not created
    assert cmd_cast(args) == 1


def test_cmd_cast_bad_schema_returns_one(tmp_env):
    tmp_env.write_text("PORT=8080\n")
    args = _make_args(tmp_env, schema="not-json")
    assert cmd_cast(args) == 1


def test_cmd_cast_error_on_bad_value_returns_one(tmp_env):
    tmp_env.write_text("PORT=notanumber\n")
    args = _make_args(tmp_env, schema='{"PORT":"int"}')
    assert cmd_cast(args) == 1


def test_cmd_cast_json_output_is_valid_json(tmp_env, capsys):
    tmp_env.write_text("PORT=9000\n")
    args = _make_args(tmp_env, schema='{"PORT":"int"}', output="json")
    cmd_cast(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["PORT"] == 9000


def test_cmd_cast_summary_output_contains_key_count(tmp_env, capsys):
    tmp_env.write_text("A=1\nB=2\n")
    args = _make_args(tmp_env)
    cmd_cast(args)
    captured = capsys.readouterr()
    assert "2 key" in captured.out


def test_build_cast_parser_registers_subcommand():
    root = argparse.ArgumentParser()
    sub = root.add_subparsers()
    build_cast_parser(sub)
    parsed = root.parse_args(["cast", "some.env"])
    assert parsed.env_file == "some.env"
