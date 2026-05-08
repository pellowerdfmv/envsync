"""Tests for envsync.masker."""
import pytest

from envsync.masker import MaskResult, _mask_value, mask_env


# ---------------------------------------------------------------------------
# _mask_value unit tests
# ---------------------------------------------------------------------------

def test_mask_value_short_string_fully_masked():
    assert _mask_value("abc", visible=4) == "***"


def test_mask_value_keeps_last_n_chars():
    result = _mask_value("supersecret", visible=4)
    assert result.endswith("cret")


def test_mask_value_uses_custom_char():
    result = _mask_value("hello", visible=2, char="#")
    assert result == "###lo"


def test_mask_value_exact_visible_length_fully_masked():
    assert _mask_value("abcd", visible=4) == "****"


# ---------------------------------------------------------------------------
# mask_env integration tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_env():
    return {
        "DB_PASSWORD": "hunter2",
        "API_KEY": "12345678",
        "APP_NAME": "myapp",
        "SECRET_TOKEN": "topsecret",
        "PORT": "5432",
        "AUTH_HEADER": None,
    }


def test_password_key_is_masked(sample_env):
    result = mask_env(sample_env)
    assert result.masked["DB_PASSWORD"] != "hunter2"
    assert "DB_PASSWORD" in result.masked_keys


def test_non_sensitive_key_unchanged(sample_env):
    result = mask_env(sample_env)
    assert result.masked["APP_NAME"] == "myapp"
    assert result.masked["PORT"] == "5432"


def test_none_value_stays_none(sample_env):
    result = mask_env(sample_env)
    assert result.masked["AUTH_HEADER"] is None
    assert "AUTH_HEADER" in result.masked_keys


def test_all_sensitive_keys_in_masked_keys(sample_env):
    result = mask_env(sample_env)
    for k in ("DB_PASSWORD", "API_KEY", "SECRET_TOKEN", "AUTH_HEADER"):
        assert k in result.masked_keys


def test_len_returns_masked_count(sample_env):
    result = mask_env(sample_env)
    assert len(result) == len(result.masked_keys)


def test_summary_format(sample_env):
    result = mask_env(sample_env)
    assert "/" in result.summary()
    assert "masked" in result.summary()


def test_extra_keys_treated_as_sensitive():
    env = {"MY_CUSTOM": "value123", "PLAIN": "hello"}
    result = mask_env(env, extra_keys=("MY_CUSTOM",))
    assert "MY_CUSTOM" in result.masked_keys
    assert result.masked["PLAIN"] == "hello"


def test_custom_visible_chars():
    env = {"API_KEY": "abcdefgh"}
    result = mask_env(env, visible=2)
    assert result.masked["API_KEY"].endswith("gh")
    assert result.masked["API_KEY"].startswith("*")


def test_original_env_not_mutated(sample_env):
    original_copy = dict(sample_env)
    mask_env(sample_env)
    assert sample_env == original_copy
