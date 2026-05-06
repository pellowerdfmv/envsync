"""Tests for envsync.tagger."""
import pytest
from envsync.tagger import TagResult, tag_env, _KNOWN_TAGS


@pytest.fixture()
def simple_env():
    return {"DB_URL": "postgres://localhost", "API_KEY": "abc123", "DEBUG": "true"}


# ---------------------------------------------------------------------------
# tag_env – basic behaviour
# ---------------------------------------------------------------------------

def test_tagged_keys_present_in_result(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required"], "API_KEY": ["secret"]})
    assert "DB_URL" in result.tags
    assert "API_KEY" in result.tags


def test_correct_tags_assigned(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required", "internal"]})
    assert result.tags["DB_URL"] == {"required", "internal"}


def test_untagged_key_absent(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required"]})
    assert "DEBUG" not in result.tags


def test_keys_with_tag_returns_matching_keys(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required"], "API_KEY": ["secret", "required"]})
    required = result.keys_with_tag("required")
    assert set(required) == {"DB_URL", "API_KEY"}


def test_keys_with_tag_empty_when_none_match(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["optional"]})
    assert result.keys_with_tag("secret") == []


def test_has_tag_true(simple_env):
    result = tag_env(simple_env, {"API_KEY": ["secret"]})
    assert result.has_tag("API_KEY", "secret") is True


def test_has_tag_false_for_missing_tag(simple_env):
    result = tag_env(simple_env, {"API_KEY": ["secret"]})
    assert result.has_tag("API_KEY", "required") is False


def test_has_tag_false_for_missing_key(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required"]})
    assert result.has_tag("NONEXISTENT", "required") is False


# ---------------------------------------------------------------------------
# strict mode
# ---------------------------------------------------------------------------

def test_unknown_tag_recorded_in_strict_mode(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["custom_label"]}, strict=True)
    assert "custom_label" in result.unknown_tags


def test_unknown_tag_not_applied_in_strict_mode(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["custom_label"]}, strict=True)
    assert "DB_URL" not in result.tags


def test_known_tag_not_in_unknown_list(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required"]}, strict=True)
    assert result.unknown_tags == []


# ---------------------------------------------------------------------------
# summary
# ---------------------------------------------------------------------------

def test_summary_contains_key(simple_env):
    result = tag_env(simple_env, {"DB_URL": ["required"]})
    assert "DB_URL" in result.summary()


def test_summary_no_tags_message(simple_env):
    result = tag_env(simple_env, {})
    assert result.summary() == "No tags defined."
