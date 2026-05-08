"""Tests for envsync.splitter."""
from __future__ import annotations

import pytest

from envsync.splitter import SplitResult, split_env


SAMPLE: dict = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "AWS_ACCESS_KEY": "AKIA…",
    "AWS_SECRET": "s3cr3t",
    "APP_DEBUG": "true",
    "UNRELATED": "value",
}

GROUPS = {
    "database": r"^DB_",
    "aws": r"^AWS_",
    "app": r"^APP_",
}


def test_keys_routed_to_correct_bucket():
    result = split_env(SAMPLE, GROUPS)
    assert "DB_HOST" in result.buckets["database"]
    assert "DB_PORT" in result.buckets["database"]
    assert "AWS_ACCESS_KEY" in result.buckets["aws"]
    assert "AWS_SECRET" in result.buckets["aws"]
    assert "APP_DEBUG" in result.buckets["app"]


def test_unmatched_key_goes_to_unmatched():
    result = split_env(SAMPLE, GROUPS)
    assert "UNRELATED" in result.unmatched


def test_unmatched_key_not_in_any_bucket():
    result = split_env(SAMPLE, GROUPS)
    for bucket in result.buckets.values():
        assert "UNRELATED" not in bucket


def test_default_bucket_captures_unmatched():
    result = split_env(SAMPLE, GROUPS, default_bucket="other")
    assert "UNRELATED" in result.buckets["other"]
    assert len(result.unmatched) == 0


def test_default_bucket_does_not_steal_matched_keys():
    result = split_env(SAMPLE, GROUPS, default_bucket="other")
    assert "DB_HOST" not in result.buckets["other"]


def test_first_match_wins():
    # Pattern overlaps: both 'all' and 'db' would match DB_ keys
    groups = {"all": r".*", "db": r"^DB_"}
    result = split_env({"DB_HOST": "localhost", "OTHER": "x"}, groups)
    assert "DB_HOST" in result.buckets["all"]
    assert "DB_HOST" not in result.buckets["db"]


def test_len_counts_non_empty_buckets():
    result = split_env(SAMPLE, GROUPS)
    assert len(result) == 3


def test_len_excludes_empty_buckets():
    groups = {"database": r"^DB_", "empty": r"^NOPE_"}
    result = split_env(SAMPLE, groups)
    assert len(result) == 1


def test_summary_lists_buckets_with_counts():
    result = split_env(SAMPLE, GROUPS)
    summary = result.summary()
    assert "database(2 keys)" in summary
    assert "aws(2 keys)" in summary
    assert "app(1 keys)" in summary


def test_summary_reports_unmatched():
    result = split_env(SAMPLE, GROUPS)
    assert "unmatched" in result.summary()


def test_values_preserved_in_buckets():
    result = split_env(SAMPLE, GROUPS)
    assert result.buckets["database"]["DB_HOST"] == "localhost"
    assert result.buckets["database"]["DB_PORT"] == "5432"


def test_none_value_preserved():
    env = {"DB_HOST": None}
    result = split_env(env, {"db": r"^DB_"})
    assert result.buckets["db"]["DB_HOST"] is None


def test_empty_env_returns_empty_result():
    result = split_env({}, GROUPS)
    for bucket in result.buckets.values():
        assert bucket == {}
    assert result.unmatched == {}
