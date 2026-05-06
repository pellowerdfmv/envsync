"""Tests for envsync.formatter."""
from __future__ import annotations

import pytest

from envsync.formatter import format_env, normalise_file


def test_simple_key_value():
    result = format_env({'DB_HOST': 'localhost'})
    assert result == 'DB_HOST=localhost\n'


def test_none_value_becomes_empty():
    result = format_env({'SECRET': None})
    assert result == 'SECRET=\n'


def test_sort_keys():
    result = format_env({'Z_KEY': 'z', 'A_KEY': 'a'}, sort_keys=True)
    lines = result.strip().splitlines()
    assert lines[0].startswith('A_KEY')
    assert lines[1].startswith('Z_KEY')


def test_sort_keys_false_preserves_order():
    result = format_env({'Z_KEY': 'z', 'A_KEY': 'a'}, sort_keys=False)
    lines = result.strip().splitlines()
    assert lines[0].startswith('Z_KEY')


def test_quote_all_wraps_plain_value():
    result = format_env({'HOST': 'localhost'}, quote_all=True)
    assert result == 'HOST="localhost"\n'


def test_quote_all_escapes_inner_quotes():
    result = format_env({'MSG': 'say "hi"'}, quote_all=True)
    assert '\\"hi\\"' in result


def test_value_with_space_auto_quoted():
    result = format_env({'MSG': 'hello world'})
    assert '"hello world"' in result


def test_value_with_hash_auto_quoted():
    result = format_env({'MSG': 'value#comment'})
    assert '"' in result


def test_uppercase_keys():
    result = format_env({'db_host': 'localhost'}, uppercase_keys=True)
    assert result.startswith('DB_HOST=')


def test_empty_dict_produces_empty_string():
    result = format_env({})
    assert result == ''


def test_normalise_file_writes_to_disk(tmp_path):
    src = str(tmp_path / 'src.env')
    dst = str(tmp_path / 'dst.env')
    parsed = {'DB_HOST': 'localhost', 'SECRET': None}
    normalise_file(src, dst, parsed, sort_keys=True)
    content = open(dst).read()
    assert 'DB_HOST=localhost' in content
    assert 'SECRET=' in content


def test_normalise_file_sort_applied(tmp_path):
    dst = str(tmp_path / 'out.env')
    parsed = {'Z': 'last', 'A': 'first'}
    normalise_file('', dst, parsed, sort_keys=True)
    lines = open(dst).read().strip().splitlines()
    assert lines[0].startswith('A=')
