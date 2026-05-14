"""Tests for envsync.freezer."""
from __future__ import annotations

import pytest

from envsync.freezer import FreezeResult, detect_drift, freeze_env


# ---------------------------------------------------------------------------
# freeze_env
# ---------------------------------------------------------------------------

def test_freeze_returns_freeze_result():
    result = freeze_env({"A": "1"})
    assert isinstance(result, FreezeResult)


def test_frozen_mapping_contains_all_keys():
    env = {"HOST": "localhost", "PORT": "5432", "DEBUG": None}
    result = freeze_env(env)
    assert set(result.frozen.keys()) == {"HOST", "PORT", "DEBUG"}


def test_frozen_mapping_is_immutable():
    result = freeze_env({"KEY": "value"})
    with pytest.raises(TypeError):
        result.frozen["KEY"] = "other"  # type: ignore[index]


def test_freeze_preserves_none_values():
    result = freeze_env({"EMPTY": None})
    assert result.frozen["EMPTY"] is None


def test_freeze_stores_source_path():
    result = freeze_env({"X": "1"}, source_path=".env.prod")
    assert result.source_path == ".env.prod"


def test_freeze_default_source_path_is_empty_string():
    result = freeze_env({})
    assert result.source_path == ""


def test_freeze_empty_env():
    result = freeze_env({})
    assert len(result.frozen) == 0


def test_no_changed_keys_after_plain_freeze():
    result = freeze_env({"A": "1"})
    assert result.changed_keys == ()
    assert result.has_changes() is False


# ---------------------------------------------------------------------------
# detect_drift
# ---------------------------------------------------------------------------

def test_no_drift_when_env_unchanged():
    env = {"A": "1", "B": "2"}
    frozen = freeze_env(env)
    result = detect_drift(frozen, dict(env))
    assert result.has_changes() is False


def test_drift_detected_for_changed_value():
    frozen = freeze_env({"HOST": "localhost"})
    result = detect_drift(frozen, {"HOST": "remotehost"})
    assert "HOST" in result.changed_keys


def test_drift_detected_for_added_key():
    frozen = freeze_env({"A": "1"})
    result = detect_drift(frozen, {"A": "1", "B": "2"})
    assert "B" in result.changed_keys


def test_drift_detected_for_removed_key():
    frozen = freeze_env({"A": "1", "B": "2"})
    result = detect_drift(frozen, {"A": "1"})
    assert "B" in result.changed_keys


def test_drift_none_to_value_counts_as_change():
    frozen = freeze_env({"SECRET": None})
    result = detect_drift(frozen, {"SECRET": "s3cr3t"})
    assert "SECRET" in result.changed_keys


def test_detect_drift_preserves_original_frozen():
    env = {"A": "1"}
    frozen = freeze_env(env)
    drifted = detect_drift(frozen, {"A": "changed"})
    assert drifted.frozen["A"] == "1"


def test_changed_keys_sorted_alphabetically():
    frozen = freeze_env({"Z": "1", "A": "1", "M": "1"})
    result = detect_drift(frozen, {"Z": "2", "A": "2", "M": "2"})
    assert list(result.changed_keys) == sorted(result.changed_keys)


# ---------------------------------------------------------------------------
# summary / has_changes
# ---------------------------------------------------------------------------

def test_summary_no_drift():
    result = freeze_env({"A": "1", "B": "2"})
    assert "no drift" in result.summary()


def test_summary_with_drift_mentions_key():
    frozen = freeze_env({"PORT": "5432"})
    result = detect_drift(frozen, {"PORT": "3306"})
    assert "PORT" in result.summary()


def test_has_changes_true_when_drift():
    frozen = freeze_env({"X": "old"})
    result = detect_drift(frozen, {"X": "new"})
    assert result.has_changes() is True
