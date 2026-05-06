"""Tests for envsync.interpolator."""

import pytest

from envsync.interpolator import InterpolationError, interpolate


def test_no_references_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    assert interpolate(env) == env


def test_brace_reference_resolved():
    env = {"BASE": "/app", "DATA": "${BASE}/data"}
    result = interpolate(env)
    assert result["DATA"] == "/app/data"


def test_bare_reference_resolved():
    env = {"USER": "admin", "DSN": "postgres://$USER@localhost"}
    result = interpolate(env)
    assert result["DSN"] == "postgres://admin@localhost"


def test_chained_references_resolved():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate(env)
    assert result["C"] == "hello_world!"


def test_none_value_stays_none():
    env = {"EMPTY": None, "OTHER": "${EMPTY}"}
    result = interpolate(env)
    assert result["EMPTY"] is None
    # None resolves to empty string in expansion
    assert result["OTHER"] == ""


def test_undefined_reference_left_as_is_non_strict():
    env = {"URL": "${UNDEFINED}/path"}
    result = interpolate(env, strict=False)
    assert result["URL"] == "${UNDEFINED}/path"


def test_undefined_reference_raises_in_strict_mode():
    env = {"URL": "${MISSING}/path"}
    with pytest.raises(InterpolationError, match="MISSING"):
        interpolate(env, strict=True)


def test_self_reference_raises():
    env = {"LOOP": "${LOOP}/suffix"}
    with pytest.raises(InterpolationError, match="Self-referencing"):
        interpolate(env)


def test_multiple_references_in_single_value():
    env = {"PROTO": "https", "HOST": "example.com", "PORT": "443"}
    env["URL"] = "${PROTO}://${HOST}:${PORT}"
    result = interpolate(env)
    assert result["URL"] == "https://example.com:443"


def test_original_mapping_not_mutated():
    env = {"A": "1", "B": "${A}"}
    original = dict(env)
    interpolate(env)
    assert env == original
