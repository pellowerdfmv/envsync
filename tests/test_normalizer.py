"""Tests for envsync.normalizer."""
from __future__ import annotations

import pytest
from pathlib import Path

from envsync.normalizer import NormalizeResult, _canonical, normalize_env, normalize_file


# ---------------------------------------------------------------------------
# _canonical helper
# ---------------------------------------------------------------------------

def test_canonical_lowercased_key():
    assert _canonical("database_host") == "DATABASE_HOST"


def test_canonical_hyphen_replaced():
    assert _canonical("db-host") == "DB_HOST"


def test_canonical_space_replaced():
    assert _canonical("db host") == "DB_HOST"


def test_canonical_already_canonical_unchanged():
    assert _canonical("DB_HOST") == "DB_HOST"


def test_canonical_strips_surrounding_whitespace():
    assert _canonical("  api_key  ") == "API_KEY"


# ---------------------------------------------------------------------------
# normalize_env
# ---------------------------------------------------------------------------

def test_normalize_env_returns_normalize_result():
    result = normalize_env({"db_host": "localhost"})
    assert isinstance(result, NormalizeResult)


def test_lowercase_key_uppercased():
    result = normalize_env({"db_host": "localhost"})
    assert "DB_HOST" in result.normalized


def test_original_lowercase_key_absent():
    result = normalize_env({"db_host": "localhost"})
    assert "db_host" not in result.normalized


def test_value_preserved_after_rename():
    result = normalize_env({"api-key": "secret"})
    assert result.normalized["API_KEY"] == "secret"


def test_none_value_preserved():
    result = normalize_env({"token": None})
    assert result.normalized["TOKEN"] is None


def test_renamed_list_contains_pair():
    result = normalize_env({"db-host": "localhost"})
    assert ("db-host", "DB_HOST") in result.renamed


def test_already_canonical_key_not_in_renamed():
    result = normalize_env({"DB_HOST": "localhost"})
    assert result.renamed == []


def test_has_changes_true_when_renamed():
    result = normalize_env({"db_host": "localhost"})
    assert result.has_changes is True


def test_has_changes_false_when_already_canonical():
    result = normalize_env({"DB_HOST": "localhost"})
    assert result.has_changes is False


def test_len_equals_key_count():
    result = normalize_env({"DB_HOST": "localhost", "API_KEY": "x"})
    assert len(result) == 2


def test_summary_mentions_renamed_count():
    result = normalize_env({"db_host": "h", "api-key": "k"})
    assert "2" in result.summary()


def test_summary_no_changes_message():
    result = normalize_env({"DB_HOST": "h"})
    assert "no changes" in result.summary()


def test_source_path_stored():
    p = Path("/tmp/test.env")
    result = normalize_env({}, source_path=p)
    assert result.source_path == p


# ---------------------------------------------------------------------------
# normalize_file
# ---------------------------------------------------------------------------

def test_normalize_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("db-host=localhost\nAPI_KEY=secret\n")
    result = normalize_file(env_file)
    assert "DB_HOST" in result.normalized
    assert "API_KEY" in result.normalized
    assert result.source_path == env_file
