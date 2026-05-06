"""Tests for envsync.redactor."""
from __future__ import annotations

import pytest

from envsync.redactor import REDACT_PLACEHOLDER, redact, sensitive_keys


@pytest.fixture()
def sample_env():
    return {
        "DB_PASSWORD": "hunter2",
        "API_KEY": "abc123",
        "HOST": "localhost",
        "PORT": "5432",
        "SECRET_TOKEN": "xyz",
        "EMPTY_SECRET": None,
    }


def test_password_is_redacted(sample_env):
    result = redact(sample_env)
    assert result["DB_PASSWORD"] == REDACT_PLACEHOLDER


def test_api_key_is_redacted(sample_env):
    result = redact(sample_env)
    assert result["API_KEY"] == REDACT_PLACEHOLDER


def test_secret_token_is_redacted(sample_env):
    result = redact(sample_env)
    assert result["SECRET_TOKEN"] == REDACT_PLACEHOLDER


def test_non_sensitive_key_unchanged(sample_env):
    result = redact(sample_env)
    assert result["HOST"] == "localhost"
    assert result["PORT"] == "5432"


def test_none_value_preserved(sample_env):
    result = redact(sample_env)
    assert result["EMPTY_SECRET"] is None


def test_custom_placeholder(sample_env):
    result = redact(sample_env, placeholder="[hidden]")
    assert result["DB_PASSWORD"] == "[hidden]"


def test_extra_patterns_respected():
    env = {"INTERNAL_CODE": "1234", "HOST": "localhost"}
    result = redact(env, extra_patterns=("code",))
    assert result["INTERNAL_CODE"] == REDACT_PLACEHOLDER
    assert result["HOST"] == "localhost"


def test_explicit_keys_always_redacted():
    env = {"CUSTOM_FIELD": "value", "ANOTHER": "data"}
    result = redact(env, explicit_keys=frozenset({"CUSTOM_FIELD"}))
    assert result["CUSTOM_FIELD"] == REDACT_PLACEHOLDER
    assert result["ANOTHER"] == "data"


def test_original_env_not_mutated(sample_env):
    original_password = sample_env["DB_PASSWORD"]
    redact(sample_env)
    assert sample_env["DB_PASSWORD"] == original_password


def test_sensitive_keys_returns_sorted_list(sample_env):
    keys = sensitive_keys(sample_env)
    assert "DB_PASSWORD" in keys
    assert "API_KEY" in keys
    assert "HOST" not in keys
    assert keys == sorted(keys)


def test_sensitive_keys_with_extra_patterns():
    env = {"INTERNAL_CODE": "1234", "DB_HOST": "localhost"}
    keys = sensitive_keys(env, extra_patterns=("code",))
    assert "INTERNAL_CODE" in keys
    assert "DB_HOST" not in keys
