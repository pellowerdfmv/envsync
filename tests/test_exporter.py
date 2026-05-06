"""Tests for envsync.exporter."""

import json
import pytest

from envsync.exporter import (
    export_env,
    export_to_json,
    export_to_shell,
    export_to_yaml,
)


SAMPLE: dict = {
    "APP_NAME": "myapp",
    "DEBUG": "true",
    "SECRET": None,
    "DATABASE_URL": "postgres://user:pass@localhost/db",
}


# ---------------------------------------------------------------------------
# JSON
# ---------------------------------------------------------------------------

def test_json_round_trips():
    result = export_to_json(SAMPLE)
    parsed = json.loads(result)
    assert parsed["APP_NAME"] == "myapp"
    assert parsed["SECRET"] is None


def test_json_is_indented():
    result = export_to_json(SAMPLE, indent=4)
    assert "    " in result


# ---------------------------------------------------------------------------
# YAML
# ---------------------------------------------------------------------------

def test_yaml_null_value():
    result = export_to_yaml({"KEY": None})
    assert "KEY: null" in result


def test_yaml_plain_value():
    result = export_to_yaml({"APP": "myapp"})
    assert "APP: myapp" in result


def test_yaml_quotes_special_chars():
    result = export_to_yaml({"URL": "http://x:8080"})
    assert result.startswith("URL: \"")


def test_yaml_multiline_output():
    result = export_to_yaml(SAMPLE)
    lines = result.splitlines()
    assert len(lines) == len(SAMPLE)


# ---------------------------------------------------------------------------
# Shell
# ---------------------------------------------------------------------------

def test_shell_has_shebang():
    result = export_to_shell(SAMPLE)
    assert result.startswith("#!/usr/bin/env sh")


def test_shell_exports_all_keys():
    result = export_to_shell(SAMPLE)
    for key in SAMPLE:
        assert f"export {key}=" in result


def test_shell_none_becomes_empty():
    result = export_to_shell({"SECRET": None})
    assert "export SECRET=''" in result


def test_shell_escapes_single_quotes():
    result = export_to_shell({"VAL": "it's"})
    assert "export VAL=" in result
    assert "'\"'\"'" in result


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def test_export_env_dispatches_json():
    result = export_env({"K": "v"}, "json")
    assert json.loads(result)["K"] == "v"


def test_export_env_dispatches_yaml():
    result = export_env({"K": "v"}, "yaml")
    assert "K: v" in result


def test_export_env_dispatches_shell():
    result = export_env({"K": "v"}, "shell")
    assert "export K=" in result


def test_export_env_case_insensitive():
    result = export_env({"K": "v"}, "JSON")
    assert json.loads(result)["K"] == "v"


def test_export_env_raises_on_unknown_format():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env({}, "toml")
