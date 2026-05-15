"""Tests for envsync.pruner."""

from __future__ import annotations

from pathlib import Path

import pytest

from envsync.pruner import PruneResult, prune_env, prune_file


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return dict(kwargs)


# ---------------------------------------------------------------------------
# prune_env – exact keys
# ---------------------------------------------------------------------------

def test_exact_key_removed():
    env = _env(DB_HOST="localhost", DB_PORT="5432", APP_NAME="myapp")
    result = prune_env(env, keys=["DB_PORT"])
    assert "DB_PORT" not in result.env


def test_exact_key_in_removed_list():
    env = _env(DB_HOST="localhost", DB_PORT="5432")
    result = prune_env(env, keys=["DB_PORT"])
    assert "DB_PORT" in result.removed_keys


def test_unrelated_keys_kept():
    env = _env(DB_HOST="localhost", DB_PORT="5432", APP_NAME="myapp")
    result = prune_env(env, keys=["DB_PORT"])
    assert "DB_HOST" in result.env
    assert "APP_NAME" in result.env


def test_multiple_exact_keys_removed():
    env = _env(A="1", B="2", C="3")
    result = prune_env(env, keys=["A", "C"])
    assert list(result.env.keys()) == ["B"]


def test_nonexistent_key_ignored():
    env = _env(A="1")
    result = prune_env(env, keys=["MISSING"])
    assert result.removed_keys == []
    assert "A" in result.env


# ---------------------------------------------------------------------------
# prune_env – patterns
# ---------------------------------------------------------------------------

def test_pattern_removes_matching_keys():
    env = _env(DB_HOST="h", DB_PORT="5432", APP_NAME="x")
    result = prune_env(env, patterns=[r"DB_.*"])
    assert "DB_HOST" not in result.env
    assert "DB_PORT" not in result.env
    assert "APP_NAME" in result.env


def test_pattern_does_not_remove_partial_match():
    # fullmatch semantics: 'DB' should NOT match 'DB_HOST'
    env = _env(DB_HOST="h", DB="x")
    result = prune_env(env, patterns=[r"DB"])
    assert "DB_HOST" in result.env
    assert "DB" not in result.env


def test_combined_keys_and_patterns():
    env = _env(DB_HOST="h", DB_PORT="p", SECRET="s", APP="a")
    result = prune_env(env, keys=["SECRET"], patterns=[r"DB_.*"])
    assert set(result.removed_keys) == {"DB_HOST", "DB_PORT", "SECRET"}
    assert list(result.env.keys()) == ["APP"]


# ---------------------------------------------------------------------------
# PruneResult helpers
# ---------------------------------------------------------------------------

def test_has_removals_true_when_keys_removed():
    env = _env(A="1", B="2")
    result = prune_env(env, keys=["A"])
    assert result.has_removals() is True


def test_has_removals_false_when_nothing_removed():
    env = _env(A="1")
    result = prune_env(env, keys=[])
    assert result.has_removals() is False


def test_len_reflects_remaining_keys():
    env = _env(A="1", B="2", C="3")
    result = prune_env(env, keys=["B"])
    assert len(result) == 2


def test_summary_no_removals():
    result = prune_env({}, keys=[])
    assert "no keys removed" in result.summary()


def test_summary_with_removals():
    env = _env(FOO="bar", BAZ="qux")
    result = prune_env(env, keys=["FOO"])
    assert "1 key" in result.summary()
    assert "FOO" in result.summary()


def test_summary_includes_source_path():
    result = prune_env({}, keys=[], source_path=Path(".env"))
    assert ".env" in result.summary()


# ---------------------------------------------------------------------------
# prune_file
# ---------------------------------------------------------------------------

def test_prune_file_reads_and_prunes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP=myapp\n")
    result = prune_file(env_file, keys=["DB_PORT"])
    assert "DB_PORT" not in result.env
    assert result.source_path == env_file


def test_prune_file_pattern(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nDB_PORT=5432\nAPP=myapp\n")
    result = prune_file(env_file, patterns=[r"DB_.*"])
    assert result.removed_keys == ["DB_HOST", "DB_PORT"]
