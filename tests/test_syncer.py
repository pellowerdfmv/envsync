"""Tests for envsync.syncer module."""

from pathlib import Path

import pytest

from envsync.syncer import generate_template, sync_missing_keys


@pytest.fixture()
def tmp_env(tmp_path: Path):
    """Helper fixture that writes a .env file and returns its path."""

    def _write(filename: str, content: str) -> Path:
        p = tmp_path / filename
        p.write_text(content, encoding="utf-8")
        return p

    return _write


# ---------------------------------------------------------------------------
# generate_template
# ---------------------------------------------------------------------------

def test_generate_template_strips_values(tmp_env):
    ref = tmp_env(".env", "APP_KEY=secret\nDB_HOST=localhost\n")
    result = generate_template(ref)
    assert "APP_KEY=" in result
    assert "DB_HOST=" in result
    assert "secret" not in result
    assert "localhost" not in result


def test_generate_template_preserves_comments(tmp_env):
    ref = tmp_env(".env", "# Database config\nDB_HOST=localhost\n")
    result = generate_template(ref)
    assert "# Database config" in result


def test_generate_template_preserves_blank_lines(tmp_env):
    ref = tmp_env(".env", "A=1\n\nB=2\n")
    result = generate_template(ref)
    lines = result.splitlines()
    assert "" in lines


def test_generate_template_no_strip(tmp_env):
    ref = tmp_env(".env", "APP_ENV=production\n")
    result = generate_template(ref, strip_values=False)
    assert "APP_ENV=production" in result


# ---------------------------------------------------------------------------
# sync_missing_keys
# ---------------------------------------------------------------------------

def test_sync_adds_missing_keys(tmp_env):
    ref = tmp_env(".env.ref", "EXISTING=1\nNEW_KEY=value\n")
    target = tmp_env(".env", "EXISTING=1\n")

    added = sync_missing_keys(ref, target)

    assert "NEW_KEY" in added
    content = target.read_text(encoding="utf-8")
    assert "NEW_KEY=" in content


def test_sync_no_missing_keys_returns_empty(tmp_env):
    ref = tmp_env(".env.ref", "KEY=1\n")
    target = tmp_env(".env", "KEY=existing\n")

    added = sync_missing_keys(ref, target)

    assert added == {}


def test_sync_uses_default_value(tmp_env):
    ref = tmp_env(".env.ref", "SECRET=abc\n")
    target = tmp_env(".env", "OTHER=1\n")

    added = sync_missing_keys(ref, target, default_value="CHANGEME")

    assert added["SECRET"] == "CHANGEME"
    content = target.read_text(encoding="utf-8")
    assert "SECRET=CHANGEME" in content


def test_sync_does_not_duplicate_existing_keys(tmp_env):
    ref = tmp_env(".env.ref", "A=1\nB=2\n")
    target = tmp_env(".env", "A=original\n")

    sync_missing_keys(ref, target)
    content = target.read_text(encoding="utf-8")

    assert content.count("A=") == 1
