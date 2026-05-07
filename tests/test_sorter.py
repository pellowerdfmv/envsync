"""Tests for envsync.sorter."""
from __future__ import annotations

import pytest

from envsync.sorter import SortResult, sort_env, _prefix


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

SAMPLE: dict = {
    "DB_HOST": "localhost",
    "APP_NAME": "envsync",
    "DB_PORT": "5432",
    "APP_ENV": "production",
    "SECRET": "abc123",
    "TIMEOUT": None,
}


# ---------------------------------------------------------------------------
# _prefix
# ---------------------------------------------------------------------------

def test_prefix_returns_segment_before_underscore():
    assert _prefix("DB_HOST") == "DB"


def test_prefix_returns_none_for_no_underscore():
    assert _prefix("SECRET") is None


def test_prefix_uses_first_underscore_only():
    assert _prefix("APP_DB_HOST") == "APP"


# ---------------------------------------------------------------------------
# sort_env — basic sorting
# ---------------------------------------------------------------------------

def test_sorted_keys_are_alphabetical():
    result = sort_env(SAMPLE)
    keys = list(result.sorted_env.keys())
    assert keys == sorted(SAMPLE.keys())


def test_sorted_keys_reverse():
    result = sort_env(SAMPLE, reverse=True)
    keys = list(result.sorted_env.keys())
    assert keys == sorted(SAMPLE.keys(), reverse=True)


def test_values_preserved_after_sort():
    result = sort_env(SAMPLE)
    for key, value in SAMPLE.items():
        assert result.sorted_env[key] == value


def test_len_equals_input_size():
    result = sort_env(SAMPLE)
    assert len(result) == len(SAMPLE)


def test_none_value_preserved():
    result = sort_env(SAMPLE)
    assert result.sorted_env["TIMEOUT"] is None


# ---------------------------------------------------------------------------
# sort_env — grouping by prefix
# ---------------------------------------------------------------------------

def test_group_by_prefix_creates_groups():
    result = sort_env(SAMPLE, group_by_prefix=True)
    assert "DB" in result.groups
    assert "APP" in result.groups


def test_group_db_contains_correct_keys():
    result = sort_env(SAMPLE, group_by_prefix=True)
    assert set(result.groups["DB"].keys()) == {"DB_HOST", "DB_PORT"}


def test_ungrouped_keys_have_no_prefix():
    result = sort_env(SAMPLE, group_by_prefix=True)
    for key in result.ungrouped:
        assert "_" not in key


def test_ungrouped_contains_secret_and_timeout():
    result = sort_env(SAMPLE, group_by_prefix=True)
    assert "SECRET" in result.ungrouped
    assert "TIMEOUT" in result.ungrouped


def test_no_grouping_by_default_all_ungrouped():
    result = sort_env(SAMPLE)
    assert result.groups == {}
    assert len(result.ungrouped) == len(SAMPLE)


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_contains_key_count():
    result = sort_env(SAMPLE)
    assert str(len(SAMPLE)) in result.summary()


def test_summary_mentions_groups_none_when_no_prefix():
    result = sort_env(SAMPLE)
    assert "none" in result.summary()


def test_summary_mentions_group_names_when_grouped():
    result = sort_env(SAMPLE, group_by_prefix=True)
    summary = result.summary()
    assert "DB" in summary
    assert "APP" in summary
