"""Tests for envsync.trimmer."""
from __future__ import annotations

import pytest

from envsync.trimmer import TrimResult, trim_env


SAMPLE: dict = {
    "APP_NAME": "myapp",
    "DB_HOST": "localhost",
    "DB_PASSWORD": "secret",
    "SECRET_KEY": "abc123",
    "DEBUG": "true",
}


# ---------------------------------------------------------------------------
# trim_env – exact key removal
# ---------------------------------------------------------------------------

def test_exact_key_removed():
    result = trim_env(SAMPLE, keys=["DEBUG"])
    assert "DEBUG" not in result.trimmed


def test_exact_key_present_in_removed_keys():
    result = trim_env(SAMPLE, keys=["DEBUG"])
    assert "DEBUG" in result.removed_keys


def test_unrelated_keys_kept_after_exact_removal():
    result = trim_env(SAMPLE, keys=["DEBUG"])
    assert "APP_NAME" in result.trimmed
    assert "DB_HOST" in result.trimmed


def test_multiple_exact_keys_removed():
    result = trim_env(SAMPLE, keys=["DEBUG", "APP_NAME"])
    assert len(result) == 2
    assert "DEBUG" not in result.trimmed
    assert "APP_NAME" not in result.trimmed


def test_nonexistent_key_ignored():
    result = trim_env(SAMPLE, keys=["DOES_NOT_EXIST"])
    assert result.removed_keys == []
    assert result.trimmed == SAMPLE


# ---------------------------------------------------------------------------
# trim_env – pattern removal
# ---------------------------------------------------------------------------

def test_pattern_removes_matching_keys():
    result = trim_env(SAMPLE, pattern=r"^DB_")
    assert "DB_HOST" not in result.trimmed
    assert "DB_PASSWORD" not in result.trimmed


def test_pattern_keeps_non_matching_keys():
    result = trim_env(SAMPLE, pattern=r"^DB_")
    assert "APP_NAME" in result.trimmed
    assert "DEBUG" in result.trimmed


def test_pattern_case_sensitive():
    result = trim_env(SAMPLE, pattern=r"^db_")
    # lowercase pattern should NOT match uppercase keys
    assert "DB_HOST" in result.trimmed


# ---------------------------------------------------------------------------
# trim_env – combined keys + pattern
# ---------------------------------------------------------------------------

def test_keys_and_pattern_combined():
    result = trim_env(SAMPLE, keys=["DEBUG"], pattern=r"SECRET")
    assert "DEBUG" not in result.trimmed
    assert "SECRET_KEY" not in result.trimmed
    assert len(result) == 2


# ---------------------------------------------------------------------------
# trim_env – validation
# ---------------------------------------------------------------------------

def test_no_args_raises_value_error():
    with pytest.raises(ValueError):
        trim_env(SAMPLE)


# ---------------------------------------------------------------------------
# TrimResult helpers
# ---------------------------------------------------------------------------

def test_has_removals_true_when_keys_removed():
    result = trim_env(SAMPLE, keys=["DEBUG"])
    assert result.has_removals() is True


def test_has_removals_false_when_nothing_removed():
    result = trim_env(SAMPLE, keys=["NONEXISTENT"])
    assert result.has_removals() is False


def test_summary_lists_removed_keys():
    result = trim_env(SAMPLE, keys=["DEBUG"])
    assert "DEBUG" in result.summary()
    assert "1" in result.summary()


def test_summary_no_removals_message():
    result = trim_env(SAMPLE, keys=["NONEXISTENT"])
    assert result.summary() == "No keys removed."


def test_original_is_unchanged():
    result = trim_env(SAMPLE, keys=["DEBUG"])
    assert result.original == SAMPLE
