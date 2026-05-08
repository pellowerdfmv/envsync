"""Edge-case tests for envsync.pinner."""
from __future__ import annotations

from envsync.pinner import pin_env


def test_empty_env_with_allow_new():
    result = pin_env({}, {"KEY": "value"}, allow_new=True)
    assert result._merged["KEY"] == "value"


def test_empty_pins_returns_unchanged_env():
    env = {"A": "1", "B": "2"}
    result = pin_env(env, {})
    assert result._merged == env
    assert len(result) == 0


def test_multiple_pins_applied_together():
    env = {"A": "old", "B": "old", "C": "keep"}
    result = pin_env(env, {"A": "new_a", "B": "new_b"})
    assert result._merged["A"] == "new_a"
    assert result._merged["B"] == "new_b"
    assert result._merged["C"] == "keep"


def test_pin_same_value_still_recorded():
    """Pinning to the existing value should still appear in pinned."""
    env = {"HOST": "localhost"}
    result = pin_env(env, {"HOST": "localhost"})
    assert "HOST" in result.pinned


def test_skipped_keys_not_in_pinned():
    env = {"A": "1"}
    result = pin_env(env, {"GHOST": "x"})
    assert "GHOST" not in result.pinned


def test_summary_no_skipped_omits_skipped_text():
    env = {"A": "1"}
    result = pin_env(env, {"A": "pinned"})
    assert "skipped" not in result.summary()


def test_source_path_appears_in_summary():
    env = {"X": "1"}
    result = pin_env(env, {"X": "v"}, source_path=".env.staging")
    assert ".env.staging" in result.summary()


def test_pin_result_len_zero_for_empty_pins():
    env = {"A": "1"}
    result = pin_env(env, {})
    assert len(result) == 0
