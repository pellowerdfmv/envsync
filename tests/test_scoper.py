"""Tests for envsync.scoper."""
from __future__ import annotations

import pytest

from envsync.scoper import ScopeResult, scope_env


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_NAME": "envsync",
        "SECRET_KEY": "abc123",
        "DEBUG": None,
    }


# ---------------------------------------------------------------------------
# scope_env
# ---------------------------------------------------------------------------

def test_included_keys_present(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"], scope="db")
    assert "DB_HOST" in result.included
    assert "DB_PORT" in result.included


def test_excluded_keys_absent_from_included(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"], scope="db")
    assert "APP_NAME" not in result.included
    assert "SECRET_KEY" not in result.included


def test_excluded_list_populated(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"], scope="db")
    assert "APP_NAME" in result.excluded
    assert "SECRET_KEY" in result.excluded
    assert "DEBUG" in result.excluded


def test_none_value_included_correctly(sample_env):
    result = scope_env(sample_env, ["DEBUG"], scope="flags")
    assert result.included["DEBUG"] is None


def test_all_keys_allowed_no_exclusions(sample_env):
    all_keys = list(sample_env.keys())
    result = scope_env(sample_env, all_keys, scope="full")
    assert not result.has_exclusions()
    assert result.excluded == []


def test_empty_allowed_excludes_everything(sample_env):
    result = scope_env(sample_env, [], scope="empty")
    assert result.included == {}
    assert len(result.excluded) == len(sample_env)


def test_len_reflects_included_count(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"], scope="db")
    assert len(result) == 2


def test_scope_label_stored(sample_env):
    result = scope_env(sample_env, ["APP_NAME"], scope="app")
    assert result.scope == "app"


def test_summary_contains_scope_name(sample_env):
    result = scope_env(sample_env, ["DB_HOST"], scope="database")
    assert "database" in result.summary()


def test_summary_contains_counts(sample_env):
    result = scope_env(sample_env, ["DB_HOST", "DB_PORT"], scope="db")
    summary = result.summary()
    assert "2" in summary  # included
    assert "3" in summary  # excluded


def test_unknown_allowed_key_ignored(sample_env):
    """Keys in allowed_keys that don't exist in env are silently ignored."""
    result = scope_env(sample_env, ["DB_HOST", "NONEXISTENT"], scope="db")
    assert "NONEXISTENT" not in result.included
    assert len(result) == 1


def test_has_exclusions_false_when_all_included(sample_env):
    result = scope_env(sample_env, list(sample_env.keys()), scope="all")
    assert result.has_exclusions() is False


def test_has_exclusions_true_when_some_excluded(sample_env):
    result = scope_env(sample_env, ["DB_HOST"], scope="tiny")
    assert result.has_exclusions() is True
