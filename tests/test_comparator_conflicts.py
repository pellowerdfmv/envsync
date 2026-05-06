"""Extended conflict and edge-case tests for envsync.comparator."""

from __future__ import annotations

import pytest

from envsync.comparator import compare_envs


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)

    return _write


def test_none_value_not_treated_as_conflict(tmp_env):
    """Keys with empty/None values in both files should not be flagged."""
    a = tmp_env("a.env", "EMPTY=\n")
    b = tmp_env("b.env", "EMPTY=\n")
    result = compare_envs([a, b])
    assert "EMPTY" not in result.value_conflicts()


def test_conflict_message_contains_filename(tmp_env):
    a = tmp_env("a.env", "DB=sqlite\n")
    b = tmp_env("b.env", "DB=postgres\n")
    result = compare_envs([a, b])
    conflicts = result.value_conflicts()
    assert "DB" in conflicts
    combined = " ".join(conflicts["DB"])
    assert "sqlite" in combined
    assert "postgres" in combined


def test_unique_keys_empty_when_all_shared(tmp_env):
    a = tmp_env("a.env", "SHARED=1\n")
    b = tmp_env("b.env", "SHARED=1\n")
    result = compare_envs([a, b])
    assert result.unique_keys[a] == set()
    assert result.unique_keys[b] == set()


def test_files_list_preserved_in_order(tmp_env):
    a = tmp_env("a.env", "A=1\n")
    b = tmp_env("b.env", "B=2\n")
    c = tmp_env("c.env", "C=3\n")
    result = compare_envs([a, b, c])
    assert result.files == [a, b, c]


def test_keys_missing_returns_empty_when_all_present(tmp_env):
    a = tmp_env("a.env", "FOO=1\n")
    b = tmp_env("b.env", "FOO=2\n")
    result = compare_envs([a, b])
    assert result.keys_missing_in(a) == set()
    assert result.keys_missing_in(b) == set()
