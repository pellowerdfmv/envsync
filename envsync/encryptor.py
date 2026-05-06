"""Simple symmetric encryption helpers for .env secret values.

Uses Fernet (AES-128-CBC + HMAC) from the *cryptography* package when
available, and falls back to a base64-based obfuscation layer so the
module is still importable in environments without the extra dependency.
"""
from __future__ import annotations

import base64
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

_FERNET_AVAILABLE = False
try:
    from cryptography.fernet import Fernet, InvalidToken  # type: ignore
    _FERNET_AVAILABLE = True
except ImportError:  # pragma: no cover
    pass


@dataclass
class EncryptResult:
    encrypted: Dict[str, Optional[str]] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)


def generate_key() -> bytes:
    """Return a new Fernet key (or a 32-byte random key as fallback)."""
    if _FERNET_AVAILABLE:
        return Fernet.generate_key()
    return base64.urlsafe_b64encode(os.urandom(32))


def _fernet_encrypt(value: str, key: bytes) -> str:
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def _fernet_decrypt(token: str, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


def _b64_encrypt(value: str, key: bytes) -> str:  # pragma: no cover
    xored = bytes(b ^ key[i % len(key)] for i, b in enumerate(value.encode()))
    return base64.urlsafe_b64encode(xored).decode()


def _b64_decrypt(token: str, key: bytes) -> str:  # pragma: no cover
    raw = base64.urlsafe_b64decode(token.encode())
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(raw)).decode()


def encrypt_env(
    env: Dict[str, Optional[str]],
    key: bytes,
    keys_to_encrypt: Optional[list[str]] = None,
) -> EncryptResult:
    """Encrypt selected (or all non-None) values in *env*."""
    result = EncryptResult()
    for k, v in env.items():
        if v is None:
            result.encrypted[k] = v
            result.skipped.append(k)
            continue
        if keys_to_encrypt is not None and k not in keys_to_encrypt:
            result.encrypted[k] = v
            continue
        fn = _fernet_encrypt if _FERNET_AVAILABLE else _b64_encrypt
        result.encrypted[k] = fn(v, key)
    return result


def decrypt_env(
    env: Dict[str, Optional[str]],
    key: bytes,
    keys_to_decrypt: Optional[list[str]] = None,
) -> Dict[str, Optional[str]]:
    """Decrypt selected (or all non-None) values in *env*."""
    out: Dict[str, Optional[str]] = {}
    for k, v in env.items():
        if v is None:
            out[k] = v
            continue
        if keys_to_decrypt is not None and k not in keys_to_decrypt:
            out[k] = v
            continue
        fn = _fernet_decrypt if _FERNET_AVAILABLE else _b64_decrypt
        try:
            out[k] = fn(v, key)
        except Exception:
            out[k] = v  # leave untouched if decryption fails
    return out
