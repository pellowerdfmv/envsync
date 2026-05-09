"""Tests for envsync.flattener."""

from __future__ import annotations

import pytest

from envsync.flattener import FlattenResult, flatten_env


# ---------------------------------------------------------------------------
# flatten_env — basic behaviour
# ---------------------------------------------------------------------------


def test_no_compound_keys_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = flatten_env(env)
    assert result.flattened == env


def test_compound_key_collapsed():
    env = {"DB__HOST": "localhost"}
    result = flatten_env(env)
    assert "DB_HOST" in result.flattened
    assert result.flattened["DB_HOST"] == "localhost"


def test_original_key_absent_after_expansion():
    env = {"DB__HOST": "localhost"}
    result = flatten_env(env)
    assert "DB__HOST" not in result.flattened


def test_triple_segment_key_collapsed():
    env = {"APP__DB__PORT": "5432"}
    result = flatten_env(env)
    assert "APP_DB_PORT" in result.flattened
    assert result.flattened["APP_DB_PORT"] == "5432"


def test_expanded_list_records_original_key():
    env = {"DB__HOST": "localhost", "PLAIN": "value"}
    result = flatten_env(env)
    assert "DB__HOST" in result.expanded
    assert "PLAIN" not in result.expanded


def test_none_value_preserved():
    env = {"DB__PASSWORD": None}
    result = flatten_env(env)
    assert result.flattened["DB_PASSWORD"] is None


def test_expand_false_keeps_original_keys():
    env = {"DB__HOST": "localhost"}
    result = flatten_env(env, expand=False)
    assert "DB__HOST" in result.flattened
    assert "DB_HOST" not in result.flattened
    assert result.expanded == []


def test_custom_delimiter():
    env = {"DB..HOST": "localhost"}
    result = flatten_env(env, delimiter="..")
    assert "DB_HOST" in result.flattened
    assert "DB..HOST" not in result.flattened


def test_custom_delimiter_no_match_unchanged():
    env = {"DB__HOST": "localhost"}
    result = flatten_env(env, delimiter="..")
    # delimiter '..' not present — key kept as-is
    assert "DB__HOST" in result.flattened


# ---------------------------------------------------------------------------
# FlattenResult helpers
# ---------------------------------------------------------------------------


def test_len_reflects_flattened_count():
    env = {"A": "1", "B__C": "2", "D": "3"}
    result = flatten_env(env)
    assert len(result) == 3


def test_has_expansions_true_when_compound_key_present():
    env = {"A__B": "x"}
    result = flatten_env(env)
    assert result.has_expansions() is True


def test_has_expansions_false_when_no_compound_keys():
    env = {"A": "x", "B": "y"}
    result = flatten_env(env)
    assert result.has_expansions() is False


def test_summary_no_expansions():
    env = {"A": "1"}
    result = flatten_env(env)
    assert "no expansions" in result.summary()


def test_summary_with_expansions():
    env = {"A__B": "1", "C": "2"}
    result = flatten_env(env)
    summary = result.summary()
    assert "expanded" in summary
    assert "__" in summary


def test_original_preserved_in_result():
    env = {"DB__HOST": "localhost"}
    result = flatten_env(env)
    assert result.original == env
    # original must not be mutated
    assert "DB__HOST" in result.original
