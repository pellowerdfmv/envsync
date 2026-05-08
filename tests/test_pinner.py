"""Tests for envsync.pinner."""
from __future__ import annotations

import pytest

from envsync.pinner import PinResult, pin_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _env(**kwargs):
    """Build a small env dict from kwargs."""
    return {k: v for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------


def test_pinned_value_overrides_original():
    env = _env(DB_HOST="localhost", DB_PORT="5432")
    result = pin_env(env, {"DB_HOST": "prod.db.example.com"})
    assert result._merged["DB_HOST"] == "prod.db.example.com"


def test_unrelated_keys_unchanged():
    env = _env(DB_HOST="localhost", SECRET="abc")
    result = pin_env(env, {"DB_HOST": "new-host"})
    assert result._merged["SECRET"] == "abc"


def test_pin_to_none_allowed():
    env = _env(API_KEY="secret")
    result = pin_env(env, {"API_KEY": None})
    assert result._merged["API_KEY"] is None


def test_pinned_recorded_in_result():
    env = _env(FOO="bar", BAZ="qux")
    result = pin_env(env, {"FOO": "pinned"})
    assert "FOO" in result.pinned
    assert "BAZ" not in result.pinned


# ---------------------------------------------------------------------------
# Skipped keys (absent from env, allow_new=False)
# ---------------------------------------------------------------------------


def test_missing_key_skipped_by_default():
    env = _env(EXISTING="yes")
    result = pin_env(env, {"MISSING_KEY": "value"})
    assert "MISSING_KEY" in result.skipped


def test_missing_key_not_added_to_merged_by_default():
    env = _env(EXISTING="yes")
    result = pin_env(env, {"MISSING_KEY": "value"})
    assert "MISSING_KEY" not in result._merged


def test_has_skipped_true_when_keys_absent():
    env = _env(A="1")
    result = pin_env(env, {"GHOST": "x"})
    assert result.has_skipped() is True


def test_has_skipped_false_when_all_found():
    env = _env(A="1", B="2")
    result = pin_env(env, {"A": "pinned"})
    assert result.has_skipped() is False


# ---------------------------------------------------------------------------
# allow_new=True
# ---------------------------------------------------------------------------


def test_allow_new_adds_absent_key():
    env = _env(EXISTING="yes")
    result = pin_env(env, {"NEW_KEY": "hello"}, allow_new=True)
    assert result._merged["NEW_KEY"] == "hello"


def test_allow_new_does_not_skip():
    env = _env(EXISTING="yes")
    result = pin_env(env, {"NEW_KEY": "hello"}, allow_new=True)
    assert "NEW_KEY" not in result.skipped


# ---------------------------------------------------------------------------
# Metadata & helpers
# ---------------------------------------------------------------------------


def test_len_reflects_pinned_count():
    env = _env(A="1", B="2", C="3")
    result = pin_env(env, {"A": "x", "B": "y"})
    assert len(result) == 2


def test_summary_contains_pinned_count():
    env = _env(X="1")
    result = pin_env(env, {"X": "locked"})
    assert "1 key(s) pinned" in result.summary()


def test_summary_mentions_skipped_when_present():
    env = _env(X="1")
    result = pin_env(env, {"GHOST": "y"})
    assert "skipped" in result.summary()


def test_source_path_stored():
    env = _env(A="1")
    result = pin_env(env, {"A": "v"}, source_path=".env.prod")
    assert result.source_path == ".env.prod"
