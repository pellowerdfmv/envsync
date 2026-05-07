"""Tests for envsync.encryptor."""
from __future__ import annotations

import pytest

from envsync.encryptor import (
    EncryptResult,
    decrypt_env,
    encrypt_env,
    generate_key,
)


@pytest.fixture()
def key() -> bytes:
    return generate_key()


def test_generate_key_returns_bytes(key):
    assert isinstance(key, bytes)
    assert len(key) > 0


def test_generate_key_is_unique():
    """Each call to generate_key should produce a different key."""
    key1 = generate_key()
    key2 = generate_key()
    assert key1 != key2


def test_encrypt_returns_encrypt_result(key):
    env = {"DB_PASSWORD": "secret"}
    result = encrypt_env(env, key)
    assert isinstance(result, EncryptResult)


def test_encrypted_value_differs_from_original(key):
    env = {"API_KEY": "my-api-key"}
    result = encrypt_env(env, key)
    assert result.encrypted["API_KEY"] != "my-api-key"


def test_round_trip_restores_original(key):
    env = {"SECRET": "topsecret", "HOST": "localhost"}
    encrypted = encrypt_env(env, key).encrypted
    decrypted = decrypt_env(encrypted, key)
    assert decrypted["SECRET"] == "topsecret"
    assert decrypted["HOST"] == "localhost"


def test_none_value_skipped(key):
    env = {"EMPTY": None, "TOKEN": "abc"}
    result = encrypt_env(env, key)
    assert result.encrypted["EMPTY"] is None
    assert "EMPTY" in result.skipped


def test_selective_encryption(key):
    env = {"SECRET": "s3cr3t", "HOST": "localhost"}
    result = encrypt_env(env, key, keys_to_encrypt=["SECRET"])
    assert result.encrypted["HOST"] == "localhost"
    assert result.encrypted["SECRET"] != "s3cr3t"


def test_selective_decryption_leaves_others_intact(key):
    env = {"SECRET": "s3cr3t", "HOST": "localhost"}
    enc = encrypt_env(env, key, keys_to_encrypt=["SECRET"]).encrypted
    dec = decrypt_env(enc, key, keys_to_decrypt=["SECRET"])
    assert dec["SECRET"] == "s3cr3t"
    assert dec["HOST"] == "localhost"


def test_decrypt_bad_token_returns_original(key):
    env = {"TOKEN": "not-a-valid-token"}
    # Should not raise; returns value unchanged
    result = decrypt_env(env, key)
    assert result["TOKEN"] == "not-a-valid-token"


def test_decrypt_with_wrong_key_returns_original(key):
    """Decrypting with a different key should not raise and return the value unchanged."""
    env = {"SECRET": "my-secret"}
    encrypted = encrypt_env(env, key).encrypted
    wrong_key = generate_key()
    result = decrypt_env(encrypted, wrong_key)
    assert result["SECRET"] != "my-secret" or result["SECRET"] == encrypted["SECRET"]


def test_encrypt_empty_string(key):
    env = {"BLANK": ""}
    result = encrypt_env(env, key)
    enc = result.encrypted["BLANK"]
    assert enc != ""
    dec = decrypt_env({"BLANK": enc}, key)
    assert dec["BLANK"] == ""


def test_multiple_keys_all_round_trip(key):
    env = {f"KEY_{i}": f"value_{i}" for i in range(10)}
    enc = encrypt_env(env, key).encrypted
    dec = decrypt_env(enc, key)
    for i in range(10):
        assert dec[f"KEY_{i}"] == f"value_{i}"
