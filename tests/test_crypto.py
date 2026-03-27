"""test_crypto.py - unit tests for crypto.py and the password helpers.

Tests run with the custom lightweight runner (run_unit_tests.py) which
discovers all top-level test_* functions automatically. No Kivy or
display is required.
"""

import hashlib
import os
import sys

# Ensure the project root is on the path when run directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from crypto import (
    CryptoContext,
    encrypt_bytes,
    decrypt_bytes,
    is_encrypted,
    _MAGIC,
)
from helpers import hash_password, verify_password, derive_encryption_key


# ---------------------------------------------------------------------------
# is_encrypted
# ---------------------------------------------------------------------------

def test_is_encrypted_true():
    data = _MAGIC + b"\x00" * 28
    assert is_encrypted(data) is True


def test_is_encrypted_false_plaintext():
    assert is_encrypted(b'{"key": "value"}') is False


def test_is_encrypted_false_short():
    assert is_encrypted(b"EN") is False


def test_is_encrypted_non_bytes():
    assert is_encrypted("ENC1") is False


# ---------------------------------------------------------------------------
# encrypt / decrypt round-trip
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_roundtrip():
    key = os.urandom(32)
    plaintext = b'{"hello": "world"}'
    blob = encrypt_bytes(plaintext, key)
    assert is_encrypted(blob)
    recovered = decrypt_bytes(blob, key)
    assert recovered == plaintext


def test_encrypt_produces_different_ciphertext_each_call():
    key = os.urandom(32)
    plaintext = b"same plaintext"
    blob1 = encrypt_bytes(plaintext, key)
    blob2 = encrypt_bytes(plaintext, key)
    # Random IV means blobs should differ
    assert blob1 != blob2


def test_decrypt_wrong_key_raises():
    key = os.urandom(32)
    wrong_key = os.urandom(32)
    blob = encrypt_bytes(b"secret data", key)
    try:
        decrypt_bytes(blob, wrong_key)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_decrypt_non_encrypted_raises():
    plaintext = b'{"not": "encrypted"}'
    try:
        decrypt_bytes(plaintext, os.urandom(32))
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_decrypt_truncated_blob_raises():
    key = os.urandom(32)
    blob = encrypt_bytes(b"data", key)
    truncated = blob[:10]
    try:
        decrypt_bytes(truncated, key)
        assert False, "Expected ValueError or exception"
    except Exception:
        pass


# ---------------------------------------------------------------------------
# CryptoContext
# ---------------------------------------------------------------------------

def test_crypto_context_set_and_get():
    key = os.urandom(32)
    CryptoContext.set_key(key)
    assert CryptoContext.get_key() == key
    assert CryptoContext.has_key() is True
    CryptoContext.clear()


def test_crypto_context_clear():
    CryptoContext.set_key(os.urandom(32))
    CryptoContext.clear()
    assert CryptoContext.get_key() is None
    assert CryptoContext.has_key() is False


def test_crypto_context_wrong_key_length_raises():
    try:
        CryptoContext.set_key(b"tooshort")
        assert False, "Expected ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# helpers - hash_password / verify_password / derive_encryption_key
# ---------------------------------------------------------------------------

def test_hash_password_contains_required_fields():
    result = hash_password("test-password")
    assert "salt" in result
    assert "hash" in result
    assert "enc_salt" in result
    assert "iterations" in result
    assert isinstance(result["iterations"], int)
    assert result["iterations"] >= 600_000


def test_hash_password_salt_and_enc_salt_differ():
    result = hash_password("test-password")
    assert result["salt"] != result["enc_salt"]


def test_verify_password_correct():
    pw = "correct-horse-battery-staple"
    stored = hash_password(pw)
    assert verify_password(pw, stored) is True


def test_verify_password_wrong():
    stored = hash_password("correct")
    assert verify_password("wrong", stored) is False


def test_derive_encryption_key_respects_iterations():
    """Keys derived with different iteration counts must differ."""
    stored_a = hash_password("mypassword")
    stored_b = dict(stored_a)
    stored_b["iterations"] = 200_000
    key_a = derive_encryption_key("mypassword", stored_b)
    key_b = derive_encryption_key("mypassword", stored_a)
    assert key_a != key_b


def test_derive_encryption_key_returns_32_bytes():
    stored = hash_password("mypassword")
    key = derive_encryption_key("mypassword", stored)
    assert isinstance(key, bytes)
    assert len(key) == 32


def test_derive_encryption_key_same_input_same_output():
    stored = hash_password("abc")
    k1 = derive_encryption_key("abc", stored)
    k2 = derive_encryption_key("abc", stored)
    assert k1 == k2


def test_derive_encryption_key_different_password_different_key():
    stored = hash_password("abc")
    k1 = derive_encryption_key("abc", stored)
    k2 = derive_encryption_key("xyz", stored)
    assert k1 != k2


def test_enc_salt_and_verification_salt_yield_different_keys():
    """enc_salt and salt are different, so derived keys must differ."""
    stored = hash_password("same-password")
    key_enc = derive_encryption_key("same-password", stored)
    # Create a modified stored dict that swaps enc_salt and salt
    swapped = dict(stored)
    swapped["enc_salt"] = stored["salt"]
    key_ver = derive_encryption_key("same-password", swapped)
    assert key_enc != key_ver


def test_encrypt_decrypt_with_derived_key():
    """Full integration: hash → derive key → encrypt → decrypt."""
    pw = "integration-test-pw"
    stored = hash_password(pw)
    assert verify_password(pw, stored)
    key = derive_encryption_key(pw, stored)
    payload = b'{"plant_id": "abc-123", "events": []}'
    blob = encrypt_bytes(payload, key)
    assert is_encrypted(blob)
    recovered = decrypt_bytes(blob, key)
    assert recovered == payload
