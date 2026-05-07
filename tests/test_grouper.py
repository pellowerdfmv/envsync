"""Tests for envsync.grouper."""
import pytest

from envsync.grouper import GroupResult, _prefix, group_env


# ---------------------------------------------------------------------------
# _prefix helper
# ---------------------------------------------------------------------------

def test_prefix_returns_segment_before_delimiter():
    assert _prefix("DB_HOST", "_") == "DB"


def test_prefix_returns_none_when_no_delimiter():
    assert _prefix("PORT", "_") is None


def test_prefix_uses_first_delimiter_only():
    assert _prefix("AWS_S3_BUCKET", "_") == "AWS"


def test_prefix_returns_none_for_leading_delimiter():
    assert _prefix("_HIDDEN", "_") is None


# ---------------------------------------------------------------------------
# group_env
# ---------------------------------------------------------------------------

SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "REDIS_URL": "redis://localhost",
    "PORT": "8080",
    "DEBUG": None,
}


def test_groups_created_by_prefix():
    result = group_env(SAMPLE)
    assert "DB" in result.groups
    assert "REDIS" in result.groups


def test_db_group_contains_correct_keys():
    result = group_env(SAMPLE)
    assert set(result.groups["DB"].keys()) == {"DB_HOST", "DB_PORT"}


def test_ungrouped_contains_keys_without_delimiter():
    result = group_env(SAMPLE)
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_values_preserved_in_groups():
    result = group_env(SAMPLE)
    assert result.groups["DB"]["DB_HOST"] == "localhost"


def test_none_value_preserved():
    result = group_env(SAMPLE)
    assert result.ungrouped["DEBUG"] is None


def test_len_counts_groups_not_ungrouped():
    result = group_env(SAMPLE)
    assert len(result) == 2  # DB, REDIS


def test_group_names_sorted():
    result = group_env(SAMPLE)
    assert result.group_names() == ["DB", "REDIS"]


def test_empty_env_returns_empty_result():
    result = group_env({})
    assert len(result) == 0
    assert result.ungrouped == {}


def test_custom_delimiter():
    env = {"APP.HOST": "example.com", "APP.PORT": "443", "VERSION": "1"}
    result = group_env(env, delimiter=".")
    assert "APP" in result.groups
    assert "VERSION" in result.ungrouped


def test_summary_contains_group_name():
    result = group_env(SAMPLE)
    assert "DB" in result.summary()
    assert "REDIS" in result.summary()


def test_summary_mentions_ungrouped():
    result = group_env(SAMPLE)
    assert "ungrouped" in result.summary()


def test_summary_empty_env():
    result = group_env({})
    assert result.summary() == "no keys"
