"""Tests for envsync.labeler."""
from __future__ import annotations

from pathlib import Path

import pytest

from envsync.labeler import LabelResult, label_env, label_env_file


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simple_env() -> dict:
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "APP_SECRET": "s3cr3t",
        "APP_DEBUG": "true",
        "UNRELATED": "value",
    }


@pytest.fixture()
def rules() -> dict:
    return {
        "database": ["DB_HOST", "DB_PORT"],
        "app": ["APP_SECRET", "APP_DEBUG"],
        "secret": ["APP_SECRET"],
    }


# ---------------------------------------------------------------------------
# LabelResult unit tests
# ---------------------------------------------------------------------------


def test_labeled_keys_present(simple_env, rules):
    result = label_env(simple_env, rules)
    assert "DB_HOST" in result.labeled
    assert "APP_SECRET" in result.labeled


def test_unlabeled_key_not_in_labeled(simple_env, rules):
    result = label_env(simple_env, rules)
    assert "UNRELATED" not in result.labeled


def test_unlabeled_key_in_unlabeled_list(simple_env, rules):
    result = label_env(simple_env, rules)
    assert "UNRELATED" in result.unlabeled


def test_multiple_labels_on_same_key(simple_env, rules):
    result = label_env(simple_env, rules)
    labels = result.labeled["APP_SECRET"]
    assert "app" in labels
    assert "secret" in labels


def test_single_label_key_has_one_label(simple_env, rules):
    result = label_env(simple_env, rules)
    assert result.labeled["DB_HOST"] == ["database"]


def test_keys_with_label_returns_matching_keys(simple_env, rules):
    result = label_env(simple_env, rules)
    db_keys = result.keys_with_label("database")
    assert set(db_keys) == {"DB_HOST", "DB_PORT"}


def test_keys_with_label_unknown_label_returns_empty(simple_env, rules):
    result = label_env(simple_env, rules)
    assert result.keys_with_label("nonexistent") == []


def test_has_labels_true_when_rules_match(simple_env, rules):
    result = label_env(simple_env, rules)
    assert result.has_labels() is True


def test_has_labels_false_when_no_rules():
    result = label_env({"FOO": "bar"}, {})
    assert result.has_labels() is False


def test_len_equals_total_keys(simple_env, rules):
    result = label_env(simple_env, rules)
    assert len(result) == len(simple_env)


def test_summary_contains_counts(simple_env, rules):
    result = label_env(simple_env, rules)
    s = result.summary()
    assert "5 keys" in s
    assert "labeled" in s


def test_source_path_stored(simple_env, rules, tmp_path):
    p = tmp_path / ".env"
    result = label_env(simple_env, rules, source_path=p)
    assert result.source_path == p


def test_source_path_in_summary(simple_env, rules, tmp_path):
    p = tmp_path / ".env"
    result = label_env(simple_env, rules, source_path=p)
    assert str(p) in result.summary()


# ---------------------------------------------------------------------------
# label_env_file integration test
# ---------------------------------------------------------------------------


def test_label_env_file_parses_and_labels(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=localhost\nAPP_KEY=abc\nOTHER=x\n")
    rules = {"database": ["DB_HOST"], "app": ["APP_KEY"]}
    result = label_env_file(env_file, rules)
    assert "DB_HOST" in result.labeled
    assert "OTHER" in result.unlabeled
    assert result.source_path == env_file
