"""Tests for envsync.stamper."""
from __future__ import annotations

import datetime
import re

import pytest

from envsync.stamper import StampResult, stamp_env


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_env():
    return {"APP_NAME": "myapp", "DEBUG": "true"}


# ---------------------------------------------------------------------------
# stamp_env — basic behaviour
# ---------------------------------------------------------------------------

def test_returns_stamp_result(simple_env):
    result = stamp_env(simple_env)
    assert isinstance(result, StampResult)


def test_original_keys_preserved(simple_env):
    result = stamp_env(simple_env, author="alice")
    assert result.env["APP_NAME"] == "myapp"
    assert result.env["DEBUG"] == "true"


def test_no_stamps_when_no_metadata(simple_env):
    result = stamp_env(simple_env)
    assert not result.has_stamps()
    assert len(result) == 0


def test_author_stamp_added(simple_env):
    result = stamp_env(simple_env, author="alice")
    assert result.env["ENVSYNC_AUTHOR"] == "alice"
    assert "ENVSYNC_AUTHOR" in result.stamps


def test_version_stamp_added(simple_env):
    result = stamp_env(simple_env, version="1.2.3")
    assert result.env["ENVSYNC_VERSION"] == "1.2.3"


def test_explicit_date_stamp_added(simple_env):
    result = stamp_env(simple_env, date="2024-01-15")
    assert result.env["ENVSYNC_DATE"] == "2024-01-15"


def test_auto_date_is_today(simple_env):
    result = stamp_env(simple_env, date="auto")
    today = datetime.date.today().isoformat()
    assert result.env["ENVSYNC_DATE"] == today


def test_all_three_stamps(simple_env):
    result = stamp_env(simple_env, author="bob", version="2.0", date="2025-06-01")
    assert len(result) == 3


# ---------------------------------------------------------------------------
# prefix customisation
# ---------------------------------------------------------------------------

def test_custom_prefix(simple_env):
    result = stamp_env(simple_env, author="carol", prefix="META")
    assert "META_AUTHOR" in result.env
    assert "ENVSYNC_AUTHOR" not in result.env


# ---------------------------------------------------------------------------
# overwrite flag
# ---------------------------------------------------------------------------

def test_overwrite_true_replaces_existing():
    env = {"ENVSYNC_AUTHOR": "old"}
    result = stamp_env(env, author="new", overwrite=True)
    assert result.env["ENVSYNC_AUTHOR"] == "new"


def test_overwrite_false_preserves_existing():
    env = {"ENVSYNC_AUTHOR": "old"}
    result = stamp_env(env, author="new", overwrite=False)
    assert result.env["ENVSYNC_AUTHOR"] == "old"
    assert "ENVSYNC_AUTHOR" not in result.stamps


# ---------------------------------------------------------------------------
# StampResult helpers
# ---------------------------------------------------------------------------

def test_has_stamps_true_when_stamps_applied(simple_env):
    result = stamp_env(simple_env, version="0.1")
    assert result.has_stamps()


def test_summary_contains_count(simple_env):
    result = stamp_env(simple_env, author="dave", version="3.0")
    assert "2" in result.summary()


def test_summary_contains_source_path(simple_env):
    result = stamp_env(simple_env, author="eve", source_path="/tmp/.env")
    assert "/tmp/.env" in result.summary()


def test_source_path_stored(simple_env):
    result = stamp_env(simple_env, source_path="prod.env")
    assert result.source_path == "prod.env"


def test_original_env_not_mutated(simple_env):
    original = dict(simple_env)
    stamp_env(simple_env, author="frank")
    assert simple_env == original
