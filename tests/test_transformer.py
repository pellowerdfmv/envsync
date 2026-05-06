"""Tests for envsync.transformer."""
from __future__ import annotations

import pytest

from envsync.transformer import (
    TransformResult,
    transform_env,
    _upper_keys,
    _strip_values,
    _remove_none,
)


# ---------------------------------------------------------------------------
# unit helpers
# ---------------------------------------------------------------------------

def test_upper_keys_lowercased():
    result = _upper_keys({"db_host": "localhost", "port": "5432"})
    assert "DB_HOST" in result
    assert "PORT" in result
    assert "db_host" not in result


def test_upper_keys_preserves_values():
    result = _upper_keys({"key": "value"})
    assert result["KEY"] == "value"


def test_strip_values_removes_whitespace():
    result = _strip_values({"A": "  hello  ", "B": "  "})
    assert result["A"] == "hello"
    assert result["B"] == ""


def test_strip_values_leaves_none_intact():
    result = _strip_values({"A": None})
    assert result["A"] is None


def test_remove_none_drops_none_values():
    result = _remove_none({"A": "ok", "B": None})
    assert "B" not in result
    assert result["A"] == "ok"


# ---------------------------------------------------------------------------
# transform_env
# ---------------------------------------------------------------------------

def test_transform_env_returns_transform_result():
    env = {"db_host": "localhost"}
    result = transform_env(env, ["upper_keys"])
    assert isinstance(result, TransformResult)


def test_transform_env_applies_steps_in_order():
    env = {"key": "  value  ", "other": None}
    result = transform_env(env, ["strip_values", "remove_none", "upper_keys"])
    assert result.transformed == {"KEY": "value", "OTHER": ""}


def test_transform_env_applied_list_matches_steps():
    steps = ["upper_keys", "strip_values"]
    result = transform_env({"a": "b"}, steps)
    assert result.applied == steps


def test_transform_env_original_unchanged():
    env = {"key": "  spaced  "}
    result = transform_env(env, ["strip_values"])
    assert result.original == {"key": "  spaced  "}


def test_transform_env_len_counts_changed_entries():
    env = {"a": "  x  ", "b": "clean"}
    result = transform_env(env, ["strip_values"])
    assert len(result) == 1  # only 'a' changed


def test_transform_env_unknown_step_raises():
    with pytest.raises(ValueError, match="Unknown transform steps"):
        transform_env({"A": "1"}, ["nonexistent"])


def test_transform_env_empty_steps_is_identity():
    env = {"X": "1", "Y": None}
    result = transform_env(env, [])
    assert result.transformed == env
    assert len(result) == 0
