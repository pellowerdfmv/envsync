"""Unit tests for envsync.parser."""

import textwrap
import pytest
from pathlib import Path

from envsync.parser import parse_env_file, _strip_quotes


@pytest.fixture()
def tmp_env(tmp_path):
    """Factory that writes content to a temp file and returns its path."""
    def _write(content: str) -> str:
        p: Path = tmp_path / '.env'
        p.write_text(textwrap.dedent(content), encoding='utf-8')
        return str(p)
    return _write


def test_basic_key_value(tmp_env):
    path = tmp_env("""
        APP_NAME=envsync
        DEBUG=true
    """)
    result = parse_env_file(path)
    assert result == {'APP_NAME': 'envsync', 'DEBUG': 'true'}


def test_quoted_values(tmp_env):
    path = tmp_env("""
        SECRET="my secret value"
        TOKEN='abc123'
    """)
    result = parse_env_file(path)
    assert result['SECRET'] == 'my secret value'
    assert result['TOKEN'] == 'abc123'


def test_empty_value_becomes_none(tmp_env):
    path = tmp_env('EMPTY_KEY=\n')
    result = parse_env_file(path)
    assert result['EMPTY_KEY'] is None


def test_comments_and_blank_lines_ignored(tmp_env):
    path = tmp_env("""
        # This is a comment
        KEY=value

        # Another comment
        OTHER=123
    """)
    result = parse_env_file(path)
    assert set(result.keys()) == {'KEY', 'OTHER'}


def test_invalid_line_raises(tmp_env):
    path = tmp_env('THIS IS INVALID\n')
    with pytest.raises(ValueError, match='Invalid syntax on line'):
        parse_env_file(path)


def test_strip_quotes_no_quotes():
    assert _strip_quotes('hello') == 'hello'


def test_strip_quotes_mismatched():
    assert _strip_quotes('"hello\'') == '"hello\''
