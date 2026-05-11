"""Tests for envsync.sanitizer."""
from __future__ import annotations

import pytest

from envsync.sanitizer import sanitize_env, SanitizeResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return {k: v for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# key sanitization
# ---------------------------------------------------------------------------

def test_lowercase_key_is_uppercased():
    result = sanitize_env({"db_host": "localhost"})
    assert "DB_HOST" in result.env


def test_original_lowercase_key_removed():
    result = sanitize_env({"db_host": "localhost"})
    assert "db_host" not in result.env


def test_hyphen_in_key_replaced_with_underscore():
    result = sanitize_env({"APP-SECRET": "abc"})
    assert "APP_SECRET" in result.env


def test_key_whitespace_stripped():
    result = sanitize_env({"  PORT  ": "8080"})
    assert "PORT" in result.env


def test_fix_keys_false_leaves_key_unchanged():
    result = sanitize_env({"db_host": "localhost"}, fix_keys=False)
    assert "db_host" in result.env
    assert "DB_HOST" not in result.env


# ---------------------------------------------------------------------------
# value sanitization
# ---------------------------------------------------------------------------

def test_value_whitespace_stripped():
    result = sanitize_env({"HOST": "  localhost  "})
    assert result.env["HOST"] == "localhost"


def test_empty_string_value_becomes_none():
    result = sanitize_env({"TOKEN": ""})
    assert result.env["TOKEN"] is None


def test_none_value_stays_none():
    result = sanitize_env({"KEY": None})
    assert result.env["KEY"] is None


def test_fix_values_false_leaves_value_unchanged():
    result = sanitize_env({"HOST": "  localhost  "}, fix_values=False)
    assert result.env["HOST"] == "  localhost  "


# ---------------------------------------------------------------------------
# change log / summary
# ---------------------------------------------------------------------------

def test_no_changes_has_no_changes():
    result = sanitize_env({"HOST": "localhost"})
    assert not result.has_changes()


def test_uppercase_change_recorded():
    result = sanitize_env({"db_host": "val"})
    assert result.has_changes()
    keys_mentioned = [entry[0] for entry in result.cleaned]
    assert "db_host" in keys_mentioned


def test_summary_no_changes():
    result = sanitize_env({"HOST": "localhost"})
    assert "No sanitization" in result.summary()


def test_summary_with_changes_mentions_count():
    result = sanitize_env({"db_host": "  val  "})
    assert "change" in result.summary()


# ---------------------------------------------------------------------------
# len / result integrity
# ---------------------------------------------------------------------------

def test_len_matches_key_count():
    result = sanitize_env({"A": "1", "B": "2", "C": "3"})
    assert len(result) == 3


def test_values_preserved_after_sanitization():
    result = sanitize_env({"api_key": "secret123"})
    assert result.env.get("API_KEY") == "secret123"
