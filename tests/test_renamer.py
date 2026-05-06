"""Tests for envsync.renamer."""

from __future__ import annotations

import pytest

from envsync.renamer import RenameResult, has_conflicts, rename_keys, summary


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _env(**kwargs):
    return {k: v for k, v in kwargs.items()}


# ---------------------------------------------------------------------------
# basic rename
# ---------------------------------------------------------------------------

def test_key_is_renamed():
    env = _env(OLD_KEY="value")
    result = rename_keys(env, {"OLD_KEY": "NEW_KEY"})
    assert "NEW_KEY" in result.env
    assert "OLD_KEY" not in result.env


def test_renamed_value_preserved():
    env = _env(DB_PASS="secret")
    result = rename_keys(env, {"DB_PASS": "DATABASE_PASSWORD"})
    assert result.env["DATABASE_PASSWORD"] == "secret"


def test_renamed_recorded_in_result():
    env = _env(A="1")
    result = rename_keys(env, {"A": "B"})
    assert result.renamed == {"A": "B"}


def test_unrelated_keys_untouched():
    env = _env(A="1", B="2", C="3")
    result = rename_keys(env, {"A": "Z"})
    assert result.env["B"] == "2"
    assert result.env["C"] == "3"


# ---------------------------------------------------------------------------
# skipped (key not present)
# ---------------------------------------------------------------------------

def test_missing_key_skipped():
    env = _env(EXISTING="x")
    result = rename_keys(env, {"MISSING": "OTHER"})
    assert "MISSING" in result.skipped


def test_skipped_does_not_alter_env():
    env = _env(EXISTING="x")
    result = rename_keys(env, {"MISSING": "OTHER"})
    assert list(result.env.keys()) == ["EXISTING"]


# ---------------------------------------------------------------------------
# conflicts
# ---------------------------------------------------------------------------

def test_conflict_when_target_key_exists():
    env = _env(OLD="v", NEW="already")
    result = rename_keys(env, {"OLD": "NEW"})
    assert "NEW" in result.conflicts


def test_conflict_preserves_original_value():
    env = _env(OLD="v", NEW="already")
    result = rename_keys(env, {"OLD": "NEW"})
    assert result.env["NEW"] == "already"
    assert result.env["OLD"] == "v"


def test_overwrite_resolves_conflict():
    env = _env(OLD="new_val", NEW="old_val")
    result = rename_keys(env, {"OLD": "NEW"}, overwrite=True)
    assert result.env["NEW"] == "new_val"
    assert not result.conflicts


def test_has_conflicts_true_when_conflict():
    env = _env(OLD="v", NEW="already")
    result = rename_keys(env, {"OLD": "NEW"})
    assert has_conflicts(result) is True


def test_has_conflicts_false_when_clean():
    env = _env(OLD="v")
    result = rename_keys(env, {"OLD": "NEW"})
    assert has_conflicts(result) is False


# ---------------------------------------------------------------------------
# multiple renames
# ---------------------------------------------------------------------------

def test_multiple_renames_applied():
    """All mappings that have no conflicts should be renamed in one pass."""
    env = _env(A="1", B="2", C="3")
    result = rename_keys(env, {"A": "X", "B": "Y", "C": "Z"})
    assert result.env == {"X": "1", "Y": "2", "Z": "3"}
    assert result.renamed == {"A": "X", "B": "Y", "C": "Z"}


def test_partial_rename_mixed_missing():
    """Keys present are renamed; missing keys are recorded in skipped."""
    env = _env(A="1", C="3")
    result = rename_keys(env, {"A": "X", "B": "Y", "C": "Z"})
    assert "X" in result.env
    assert "Z" in result.env
    assert "B" in result.skipped
    assert len(result.renamed) == 2


# ---------------------------------------------------------------------------
# summary
# -----------------
