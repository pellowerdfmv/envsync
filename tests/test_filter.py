"""Tests for envsync.filter."""
import pytest
from envsync.filter import filter_env, FilterResult


SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "APP_SECRET": "abc123",
    "APP_DEBUG": "",
    "REDIS_URL": None,
    "LOG_LEVEL": "info",
}


def test_no_filters_returns_all_keys():
    result = filter_env(SAMPLE)
    assert set(result.matched.keys()) == set(SAMPLE.keys())
    assert result.excluded == {}


def test_pattern_matches_db_keys():
    result = filter_env(SAMPLE, pattern=r"^DB_")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_pattern_excludes_non_matching():
    result = filter_env(SAMPLE, pattern=r"^DB_")
    assert "APP_SECRET" in result.excluded
    assert "REDIS_URL" in result.excluded


def test_prefix_filters_app_keys():
    result = filter_env(SAMPLE, prefix="APP_")
    assert set(result.matched.keys()) == {"APP_SECRET", "APP_DEBUG"}


def test_set_only_excludes_none_and_empty():
    result = filter_env(SAMPLE, set_only=True)
    assert "REDIS_URL" not in result.matched   # None
    assert "APP_DEBUG" not in result.matched   # empty string
    assert "DB_HOST" in result.matched


def test_unset_only_returns_none_values():
    result = filter_env(SAMPLE, unset_only=True)
    assert set(result.matched.keys()) == {"REDIS_URL"}


def test_set_only_and_unset_only_raises():
    with pytest.raises(ValueError, match="mutually exclusive"):
        filter_env(SAMPLE, set_only=True, unset_only=True)


def test_pattern_and_prefix_combined():
    env = {"DB_HOST": "x", "DB_BACKUP_HOST": "y", "APP_DB": "z"}
    result = filter_env(env, pattern=r"DB", prefix="DB_")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_BACKUP_HOST"}
    assert "APP_DB" in result.excluded


def test_len_reflects_matched_count():
    result = filter_env(SAMPLE, pattern=r"^DB_")
    assert len(result) == 2


def test_summary_contains_pattern():
    result = filter_env(SAMPLE, pattern=r"^DB_")
    assert "re:^DB_" in result.summary()


def test_summary_contains_counts():
    result = filter_env(SAMPLE, prefix="DB_")
    assert "2/" in result.summary()


def test_empty_env_returns_empty_result():
    result = filter_env({})
    assert result.matched == {}
    assert result.excluded == {}
