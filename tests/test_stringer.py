"""Tests for envsync.stringer."""
from __future__ import annotations

import pytest

from envsync.stringer import StringResult, stringify_env


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

SIMPLE: dict = {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": None}


# ---------------------------------------------------------------------------
# StringResult
# ---------------------------------------------------------------------------

def test_len_equals_key_count():
    result = stringify_env(SIMPLE)
    assert len(result) == 3


def test_summary_contains_format():
    result = stringify_env(SIMPLE, fmt="export")
    assert "export" in result.summary()


def test_summary_contains_key_count():
    result = stringify_env(SIMPLE)
    assert "3" in result.summary()


def test_summary_contains_source_path():
    result = stringify_env(SIMPLE, source_path=".env.test")
    assert ".env.test" in result.summary()


def test_summary_no_source_path_omits_parens():
    result = stringify_env(SIMPLE)
    assert "(" not in result.summary()


# ---------------------------------------------------------------------------
# dotenv format
# ---------------------------------------------------------------------------

def test_dotenv_plain_value():
    result = stringify_env({"KEY": "value"})
    assert "KEY=value" in result.content


def test_dotenv_none_value_becomes_empty_assignment():
    result = stringify_env({"KEY": None})
    assert "KEY=" in result.content


def test_dotenv_value_with_space_is_quoted():
    result = stringify_env({"MSG": "hello world"})
    assert 'MSG="hello world"' in result.content


def test_dotenv_value_with_hash_is_quoted():
    result = stringify_env({"TAG": "v1#rc1"})
    assert '"' in result.content


def test_dotenv_multiple_keys_newline_separated():
    result = stringify_env({"A": "1", "B": "2"})
    assert "\n" in result.content


# ---------------------------------------------------------------------------
# export format
# ---------------------------------------------------------------------------

def test_export_starts_with_export_keyword():
    result = stringify_env({"HOST": "db"}, fmt="export")
    assert result.content.startswith("export ")


def test_export_none_becomes_empty_single_quotes():
    result = stringify_env({"KEY": None}, fmt="export")
    assert "export KEY=''" in result.content


def test_export_value_wrapped_in_single_quotes():
    result = stringify_env({"HOST": "localhost"}, fmt="export")
    assert "export HOST='localhost'" in result.content


def test_export_single_quote_in_value_escaped():
    result = stringify_env({"MSG": "it's fine"}, fmt="export")
    # should not contain unescaped single-quote-terminated string
    assert "it'\"'\"'s fine" in result.content


# ---------------------------------------------------------------------------
# inline format
# ---------------------------------------------------------------------------

def test_inline_no_newlines():
    result = stringify_env({"A": "1", "B": "2"}, fmt="inline")
    assert "\n" not in result.content


def test_inline_none_value_becomes_empty():
    result = stringify_env({"KEY": None}, fmt="inline")
    assert "KEY=" in result.content


def test_inline_keys_space_separated():
    result = stringify_env({"A": "1", "B": "2"}, fmt="inline")
    assert result.content == "A=1 B=2"


# ---------------------------------------------------------------------------
# error handling
# ---------------------------------------------------------------------------

def test_unknown_format_raises_value_error():
    with pytest.raises(ValueError, match="Unknown format"):
        stringify_env({"K": "v"}, fmt="xml")


def test_empty_env_returns_empty_string():
    result = stringify_env({})
    assert result.content == ""
    assert len(result) == 0
