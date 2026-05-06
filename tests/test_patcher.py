"""Tests for envsync.patcher."""
from __future__ import annotations

from typing import Dict, Optional

import pytest

from envsync.patcher import PatchResult, patch_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env() -> Dict[str, Optional[str]]:
    return {"HOST": "localhost", "PORT": "5432", "DEBUG": "true", "SECRET": None}


# ---------------------------------------------------------------------------
# Basic patching
# ---------------------------------------------------------------------------

def test_patched_value_is_updated():
    result = patch_env(_env(), {"HOST": "prod.example.com"})
    assert result.patched["HOST"] == "prod.example.com"


def test_unrelated_keys_unchanged():
    result = patch_env(_env(), {"PORT": "9999"})
    assert result.patched["HOST"] == "localhost"
    assert result.patched["DEBUG"] == "true"


def test_patch_to_none_allowed():
    result = patch_env(_env(), {"DEBUG": None})
    assert result.patched["DEBUG"] is None


def test_patch_none_to_value():
    result = patch_env(_env(), {"SECRET": "s3cr3t"})
    assert result.patched["SECRET"] == "s3cr3t"


# ---------------------------------------------------------------------------
# Applied / skipped tracking
# ---------------------------------------------------------------------------

def test_applied_records_old_and_new():
    result = patch_env(_env(), {"PORT": "6543"})
    assert len(result.applied) == 1
    key, old, new = result.applied[0]
    assert key == "PORT"
    assert old == "5432"
    assert new == "6543"


def test_missing_key_skipped_by_default():
    result = patch_env(_env(), {"UNKNOWN": "value"})
    assert "UNKNOWN" not in result.patched
    assert "UNKNOWN" in result.skipped


def test_missing_key_added_when_flag_set():
    result = patch_env(_env(), {"NEW_KEY": "hello"}, add_missing=True)
    assert result.patched["NEW_KEY"] == "hello"
    assert any(k == "NEW_KEY" for k, _, _ in result.applied)


def test_has_changes_true_when_patched():
    result = patch_env(_env(), {"HOST": "other"})
    assert result.has_changes() is True


def test_has_changes_false_when_all_skipped():
    result = patch_env(_env(), {"GHOST": "value"})
    assert result.has_changes() is False


# ---------------------------------------------------------------------------
# Source env is not mutated
# ---------------------------------------------------------------------------

def test_original_env_not_mutated():
    original = _env()
    patch_env(original, {"HOST": "changed"})
    assert original["HOST"] == "localhost"


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

def test_summary_mentions_patched_count():
    result = patch_env(_env(), {"HOST": "x", "PORT": "1"})
    assert "2 key(s) patched" in result.summary()


def test_summary_no_changes_message():
    result = patch_env(_env(), {"GHOST": "x"})
    assert "No keys patched" in result.summary()


def test_summary_mentions_skipped():
    result = patch_env(_env(), {"GHOST": "x"})
    assert "GHOST" in result.summary()
