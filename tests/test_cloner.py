"""Tests for envsync.cloner."""
from __future__ import annotations

import pytest

from envsync.cloner import CloneResult, clone_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return {k: (v if v != "__none__" else None) for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# Basic cloning
# ---------------------------------------------------------------------------

def test_clone_returns_clone_result():
    result = clone_env({"A": "1"})
    assert isinstance(result, CloneResult)


def test_clone_copies_all_keys():
    src = _env(A="1", B="2", C="3")
    result = clone_env(src)
    assert set(result.cloned.keys()) == {"A", "B", "C"}


def test_clone_preserves_values():
    src = _env(HOST="localhost", PORT="5432")
    result = clone_env(src)
    assert result.cloned["HOST"] == "localhost"
    assert result.cloned["PORT"] == "5432"


def test_clone_preserves_none_values():
    src = {"KEY": None}
    result = clone_env(src)
    assert result.cloned["KEY"] is None


def test_clone_is_independent_copy():
    src = {"X": "original"}
    result = clone_env(src)
    result.cloned["X"] = "mutated"
    assert src["X"] == "original"


# ---------------------------------------------------------------------------
# Remapping
# ---------------------------------------------------------------------------

def test_remap_renames_key():
    result = clone_env({"OLD": "val"}, remap={"OLD": "NEW"})
    assert "NEW" in result.cloned
    assert "OLD" not in result.cloned


def test_remap_preserves_value():
    result = clone_env({"OLD": "kept"}, remap={"OLD": "NEW"})
    assert result.cloned["NEW"] == "kept"


def test_remap_recorded_in_result():
    result = clone_env({"A": "1"}, remap={"A": "Z"})
    assert result.remapped == {"A": "Z"}


def test_unremapped_key_not_in_remapped():
    result = clone_env({"A": "1", "B": "2"}, remap={"A": "Z"})
    assert "B" not in result.remapped


def test_has_remaps_true_when_remap_applied():
    result = clone_env({"K": "v"}, remap={"K": "K2"})
    assert result.has_remaps() is True


def test_has_remaps_false_without_remap():
    result = clone_env({"K": "v"})
    assert result.has_remaps() is False


# ---------------------------------------------------------------------------
# Overrides
# ---------------------------------------------------------------------------

def test_override_changes_value():
    result = clone_env({"DB": "old"}, overrides={"DB": "new"})
    assert result.cloned["DB"] == "new"


def test_override_to_none_allowed():
    result = clone_env({"DB": "old"}, overrides={"DB": None})
    assert result.cloned["DB"] is None


def test_override_nonexistent_key_ignored():
    result = clone_env({"A": "1"}, overrides={"MISSING": "x"})
    assert "MISSING" not in result.cloned
    assert result.overridden == {}


def test_has_overrides_true_when_applied():
    result = clone_env({"A": "1"}, overrides={"A": "2"})
    assert result.has_overrides() is True


def test_has_overrides_false_without_overrides():
    result = clone_env({"A": "1"})
    assert result.has_overrides() is False


# ---------------------------------------------------------------------------
# Summary & len
# ---------------------------------------------------------------------------

def test_len_equals_number_of_cloned_keys():
    result = clone_env({"A": "1", "B": "2"})
    assert len(result) == 2


def test_summary_contains_key_count():
    result = clone_env({"A": "1", "B": "2"})
    assert "2" in result.summary()


def test_summary_mentions_remapped():
    result = clone_env({"A": "1"}, remap={"A": "Z"})
    assert "remapped" in result.summary()


def test_summary_mentions_overridden():
    result = clone_env({"A": "1"}, overrides={"A": "2"})
    assert "overridden" in result.summary()
