"""Edge-case tests for envsync.scoper."""
from __future__ import annotations

from envsync.scoper import scope_env


def test_empty_env_returns_empty_included():
    result = scope_env({}, ["DB_HOST"], scope="db")
    assert result.included == {}
    assert result.excluded == []


def test_empty_env_no_exclusions():
    result = scope_env({}, [], scope="empty")
    assert result.has_exclusions() is False


def test_duplicate_allowed_keys_deduplicated():
    """Repeated keys in allowed list should not cause duplicate entries."""
    env = {"DB_HOST": "localhost", "APP": "test"}
    result = scope_env(env, ["DB_HOST", "DB_HOST"], scope="db")
    assert len(result.included) == 1
    assert result.included["DB_HOST"] == "localhost"


def test_value_preserved_exactly():
    env = {"SECRET": "p@$$w0rd!"}
    result = scope_env(env, ["SECRET"], scope="secrets")
    assert result.included["SECRET"] == "p@$$w0rd!"


def test_len_zero_when_nothing_included():
    env = {"APP": "test"}
    result = scope_env(env, ["MISSING"], scope="x")
    assert len(result) == 0


def test_summary_is_string():
    env = {"A": "1"}
    result = scope_env(env, ["A"], scope="s")
    assert isinstance(result.summary(), str)


def test_order_of_included_matches_source_order():
    """Insertion order of the source env is preserved in included."""
    env = {"Z": "26", "A": "1", "M": "13"}
    result = scope_env(env, ["Z", "A", "M"], scope="all")
    assert list(result.included.keys()) == ["Z", "A", "M"]
