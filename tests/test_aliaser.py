"""Tests for envsync.aliaser."""
from __future__ import annotations

import pytest

from envsync.aliaser import AliasResult, alias_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return {k: v for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# Basic behaviour
# ---------------------------------------------------------------------------

def test_alias_creates_new_key():
    env = _env(DB_HOST="localhost")
    result = alias_env(env, {"DATABASE_HOST": "DB_HOST"})
    assert "DATABASE_HOST" in result.env


def test_alias_copies_value():
    env = _env(DB_HOST="localhost")
    result = alias_env(env, {"DATABASE_HOST": "DB_HOST"})
    assert result.env["DATABASE_HOST"] == "localhost"


def test_original_kept_by_default():
    env = _env(DB_HOST="localhost")
    result = alias_env(env, {"DATABASE_HOST": "DB_HOST"})
    assert "DB_HOST" in result.env


def test_original_removed_when_keep_false():
    env = _env(DB_HOST="localhost")
    result = alias_env(env, {"DATABASE_HOST": "DB_HOST"}, keep_original=False)
    assert "DB_HOST" not in result.env


def test_aliased_dict_records_mapping():
    env = _env(DB_HOST="localhost")
    result = alias_env(env, {"DATABASE_HOST": "DB_HOST"})
    assert result.aliased == {"DATABASE_HOST": "DB_HOST"}


def test_missing_source_key_recorded():
    env = _env(UNRELATED="val")
    result = alias_env(env, {"NEW_KEY": "MISSING_KEY"})
    assert "MISSING_KEY" in result.missing


def test_missing_source_key_not_added_to_env():
    env = _env(UNRELATED="val")
    result = alias_env(env, {"NEW_KEY": "MISSING_KEY"})
    assert "NEW_KEY" not in result.env


def test_none_value_aliased_correctly():
    env: dict = {"SECRET": None}
    result = alias_env(env, {"APP_SECRET": "SECRET"})
    assert result.env["APP_SECRET"] is None


def test_multiple_aliases_applied():
    env = _env(A="1", B="2")
    result = alias_env(env, {"ALPHA": "A", "BETA": "B"})
    assert result.env["ALPHA"] == "1"
    assert result.env["BETA"] == "2"


def test_unrelated_keys_unchanged():
    env = _env(A="1", OTHER="keep")
    result = alias_env(env, {"ALPHA": "A"})
    assert result.env["OTHER"] == "keep"


# ---------------------------------------------------------------------------
# AliasResult helpers
# ---------------------------------------------------------------------------

def test_len_reflects_env_size():
    env = _env(A="1", B="2")
    result = alias_env(env, {"ALPHA": "A"})
    assert len(result) == len(result.env)


def test_has_missing_true_when_source_absent():
    env = _env(X="1")
    result = alias_env(env, {"Y": "GHOST"})
    assert result.has_missing() is True


def test_has_missing_false_when_all_present():
    env = _env(X="1")
    result = alias_env(env, {"Y": "X"})
    assert result.has_missing() is False


def test_summary_contains_alias_count():
    env = _env(A="1", B="2")
    result = alias_env(env, {"ALPHA": "A", "BETA": "B"})
    assert "2 alias" in result.summary()


def test_summary_mentions_missing_when_present():
    env = _env(A="1")
    result = alias_env(env, {"X": "NOPE"})
    assert "not found" in result.summary()


def test_empty_aliases_dict_leaves_env_unchanged():
    env = _env(A="1", B="2")
    result = alias_env(env, {})
    assert result.env == env
    assert result.aliased == {}
    assert result.missing == []
