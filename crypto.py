"""crypto.py - AES-256-GCM encryption helpers for Magic Herb Tracker.

All sensitive data files (garden/*.json, plants/*.json, plants_index.json)
are encrypted at rest when a password has been set. settings.json is
deliberately left plaintext so the app can bootstrap language / shader /
path config before a user unlocks the screen.

File format produced by encrypt_bytes():
    b"ENC1" (4-byte magic)
    iv (12 bytes, random)
    ciphertext + GCM tag (variable length)

If no key is loaded (password-free mode) all data is stored as plain JSON.
"""

import logging
from typing import Optional

import crypto_rs

LOG = logging.getLogger(__name__)

_MAGIC = b"ENC1"
_IV_LEN = 12 # 96-bit nonce recommended for GCM


class CryptoContext:
    """Process-wide singleton that holds the active encryption key.

    Call ``set_key()`` after a successful password unlock.
    Call ``clear()`` if the password is removed.
    """

    _key: Optional[bytearray] = None

    @classmethod
    def set_key(cls, key: bytes) -> None:
        """Store the 32-byte AES-256 key derived from the user's password."""
        if len(key) != 32:
            raise ValueError(f"Key must be 32 bytes, got {len(key)}")
        # Zero the old key before replacing it
        if cls._key is not None:
            for i in range(len(cls._key)):
                cls._key[i] = 0
        cls._key = bytearray(key)

    @classmethod
    def get_key(cls) -> Optional[bytes]:
        """Return the active key, or None if no password is loaded."""
        return bytes(cls._key) if cls._key is not None else None

    @classmethod
    def clear(cls) -> None:
        """Zero and drop the key (password removed / app locked)."""
        if cls._key is not None:
            for i in range(len(cls._key)):
                cls._key[i] = 0
        cls._key = None

    @classmethod
    def has_key(cls) -> bool:
        return cls._key is not None


def is_encrypted(data: bytes) -> bool:
    """Return True if *data* begins with the ENC1 magic header."""
    return isinstance(data, bytes) and data[:4] == _MAGIC


def encrypt_bytes(plaintext: bytes, key: bytes, aad: Optional[bytes] = None) -> bytes:
    """Encrypt *plaintext* with AES-256-GCM using a random IV.

    *aad* (Additional Authenticated Data) binds the ciphertext to a context
    (e.g. filename) so it cannot be silently swapped to a different location.
    Returns the ENC1-prefixed binary blob.
    """
    return bytes(crypto_rs.encrypt_bytes(plaintext, key, aad))


def decrypt_bytes(data: bytes, key: bytes, aad: Optional[bytes] = None) -> bytes:
    """Decrypt an ENC1-prefixed blob. Raises ``ValueError`` on auth failure.

    *aad* must match the value used during encryption.
    """
    return bytes(crypto_rs.decrypt_bytes(data, key, aad))
