"""Unit tests for password hashing and JWT — pure functions, no DB."""
import time

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token, decode_access_token, hash_password, verify_password,
)


def test_hash_is_not_plaintext_and_verifies():
    h = hash_password("secret123")
    assert h != "secret123"
    assert verify_password("secret123", h)


def test_wrong_password_fails_verification():
    h = hash_password("secret123")
    assert not verify_password("wrong", h)


def test_same_password_produces_different_hashes():
    assert hash_password("x") != hash_password("x")  # salted


def test_token_roundtrip_contains_subject():
    token = create_access_token(subject=42)
    payload = decode_access_token(token)
    assert payload["sub"] == "42"


def test_tampered_token_rejected():
    token = create_access_token(subject=1)
    with pytest.raises(jwt.PyJWTError):
        decode_access_token(token + "tampered")


def test_expired_token_rejected():
    token = create_access_token(subject=1, expires_minutes=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)
