"""Tests for envsync.caster."""
import pytest

from envsync.caster import CastResult, cast_env, _cast_value


# ---------------------------------------------------------------------------
# _cast_value unit tests
# ---------------------------------------------------------------------------

def test_cast_str_returns_string():
    assert _cast_value("hello", "str") == "hello"


def test_cast_int_valid():
    assert _cast_value("42", "int") == 42


def test_cast_int_invalid_raises():
    with pytest.raises(ValueError):
        _cast_value("abc", "integer")


def test_cast_float_valid():
    assert _cast_value("3.14", "float") == pytest.approx(3.14)


def test_cast_bool_true_variants():
    for raw in ("1", "true", "True", "TRUE", "yes", "on"):
        assert _cast_value(raw, "bool") is True


def test_cast_bool_false_variants():
    for raw in ("0", "false", "False", "no", "off"):
        assert _cast_value(raw, "bool") is False


def test_cast_bool_invalid_raises():
    with pytest.raises(ValueError):
        _cast_value("maybe", "boolean")


def test_cast_list_comma_separated():
    result = _cast_value("a,b,c", "list")
    assert result == ["a", "b", "c"]


def test_cast_list_trims_whitespace():
    result = _cast_value(" x , y , z ", "list")
    assert result == ["x", "y", "z"]


def test_cast_none_returns_none():
    assert _cast_value(None, "int") is None


def test_cast_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown type hint"):
        _cast_value("val", "uuid")


# ---------------------------------------------------------------------------
# cast_env integration tests
# ---------------------------------------------------------------------------

def test_cast_env_applies_schema():
    env = {"PORT": "8080", "DEBUG": "true", "NAME": "app"}
    schema = {"PORT": "int", "DEBUG": "bool"}
    result = cast_env(env, schema)
    assert result.values["PORT"] == 8080
    assert result.values["DEBUG"] is True
    assert result.values["NAME"] == "app"


def test_cast_env_no_schema_passes_through():
    env = {"FOO": "bar"}
    result = cast_env(env, {})
    assert result.values["FOO"] == "bar"
    assert not result.has_errors()


def test_cast_env_records_error_on_bad_value():
    env = {"PORT": "not_a_number"}
    result = cast_env(env, {"PORT": "int"})
    assert result.has_errors()
    assert "PORT" in result.errors


def test_cast_env_keeps_original_on_error():
    env = {"PORT": "bad"}
    result = cast_env(env, {"PORT": "int"})
    assert result.values["PORT"] == "bad"


def test_cast_env_len_counts_all_keys():
    env = {"A": "1", "B": "2", "C": "3"}
    result = cast_env(env, {})
    assert len(result) == 3


def test_cast_env_summary_no_errors():
    result = cast_env({"X": "1"}, {})
    assert "1 key" in result.summary()
    assert "error" not in result.summary()


def test_cast_env_summary_with_errors():
    result = cast_env({"X": "bad"}, {"X": "int"})
    assert "error" in result.summary()
