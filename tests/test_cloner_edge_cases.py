"""Edge-case tests for envsync.cloner."""
from __future__ import annotations

from envsync.cloner import clone_env


def test_empty_env_returns_empty_clone():
    result = clone_env({})
    assert result.cloned == {}


def test_empty_env_len_is_zero():
    result = clone_env({})
    assert len(result) == 0


def test_remap_and_override_combined():
    """Key is first renamed, then the override uses the *new* name."""
    result = clone_env(
        {"OLD": "original"},
        remap={"OLD": "NEW"},
        overrides={"NEW": "patched"},
    )
    assert result.cloned["NEW"] == "patched"
    assert result.remapped == {"OLD": "NEW"}
    assert result.overridden == {"NEW": "patched"}


def test_remap_unknown_key_is_silently_ignored():
    """A remap entry for a key absent in env has no effect."""
    result = clone_env({"A": "1"}, remap={"GHOST": "SPIRIT"})
    assert set(result.cloned.keys()) == {"A"}
    assert result.remapped == {}


def test_multiple_remaps_applied():
    result = clone_env(
        {"A": "1", "B": "2"},
        remap={"A": "ALPHA", "B": "BETA"},
    )
    assert "ALPHA" in result.cloned
    assert "BETA" in result.cloned
    assert len(result.remapped) == 2


def test_multiple_overrides_applied():
    result = clone_env(
        {"X": "a", "Y": "b"},
        overrides={"X": "aa", "Y": "bb"},
    )
    assert result.cloned["X"] == "aa"
    assert result.cloned["Y"] == "bb"


def test_summary_no_changes_is_concise():
    result = clone_env({"K": "v"})
    summary = result.summary()
    assert "remapped" not in summary
    assert "overridden" not in summary


def test_clone_does_not_mutate_source():
    src = {"A": "1", "B": "2"}
    clone_env(src, remap={"A": "Z"}, overrides={"Z": "new"})
    assert src == {"A": "1", "B": "2"}
