"""weed_format.py - .weed binary file format for Magic Herb Tracker.

Binary layout
-------------
Offset Size Field
-------- ----- ------------------------------------------------------
 0 4 Magic: b"WEED"
 4 1 Version: 0x01
 5 1 Flags: bit0 = encrypted, bit1 = compressed (bit1 always set)
 6 2 num_sections (uint16 LE)
 8 16 export_salt (16 random bytes when encrypted, zeros otherwise)
-- per-section record (repeated num_sections times) ------------------
+0 2 section_type (uint16 LE)
               0x0001 MANIFEST – export metadata (JSON)
               0x0002 GARDEN – full garden dict incl. plants array (JSON)
               0x0003 EVENTS – per-plant event log (JSON)
+2 16 uuid_bytes (16 raw bytes from UUID; zero-filled for MANIFEST)
+18 4 payload_length (uint32 LE)
+22 N payload bytes
-- footer ------------------------------------------------------------
EOF-32 32 SHA-256 of every byte above this field

Payload layout
--------------
Unencrypted: zlib.compress(json_bytes, level=6)
Encrypted: IV (12 bytes, random per section) + AESGCM(key).encrypt(IV, zlib.compress(json_bytes))

Key derivation (encrypted exports):
    key = PBKDF2-HMAC-SHA256(export_password, export_salt, 600_000 iters, dklen=32)

The DB encryption key (CryptoContext) is never consulted here - export files
use their own completely independent key derived from the export password.
Data is always exported/imported as plaintext JSON payloads regardless of
whether the live database is encrypted. The storage layer's transparent
decrypt handles reading from the DB; the .weed writer/reader only deals with
raw JSON dicts.
"""

from __future__ import annotations

import hmac as _hmac
import json
import os
import struct
import uuid
import zlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import crypto_rs

__all__ = [
    "write_weed",
    "read_weed",
    "WeedPasswordRequired",
    "WeedWrongPassword",
    "WeedCorrupted",
    "WEED_EXT",
]

# -- format constants ----------------------------------------------------------

WEED_MAGIC = b"WEED"
WEED_VERSION = 0x02
WEED_EXT = ".weed"

FLAG_ENCRYPTED = 0x01
FLAG_COMPRESSED = 0x02

SECT_MANIFEST = 0x0001
SECT_GARDEN = 0x0002
SECT_EVENTS = 0x0003

APP_VERSION = "0.1.0"
_PBKDF2_ITERS = 600_000
_IV_LEN = 12 # 96-bit GCM nonce

# HMAC key used to checksum *unencrypted* .weed files.
# For encrypted files each section already has AES-GCM authentication;
_APP_HMAC_KEY = b"magic-herb-tracker-open-export-v1-integrity-2026"

# Struct formats (little-endian)
# Header: magic(4s) version(B) flags(B) num_sections(H) export_salt(16s) = 24 bytes
_HDR = struct.Struct("<4sBBH16s")
# Section: type(H) uuid_bytes(16s) payload_len(I) = 22 bytes
_SECT = struct.Struct("<H16sI")


# -- exceptions ----------------------------------------------------------------

class WeedPasswordRequired(Exception):
    """The .weed file is encrypted but no export password was supplied."""

class WeedWrongPassword(Exception):
    """Export password supplied but decryption failed (wrong key / corrupt)."""

class WeedCorrupted(Exception):
    """File integrity check failed or structural parse error."""


# -- internal helpers ----------------------------------------------------------

def _uuid_to_bytes(uid: str) -> bytes:
    try:
        return uuid.UUID(str(uid)).bytes
    except (ValueError, AttributeError):
        return b"\x00" * 16


def _bytes_to_uuid(b: bytes) -> str:
    try:
        return str(uuid.UUID(bytes=b))
    except (ValueError, AttributeError):
        return ""


def _derive_key(password: str, salt: bytes) -> bytes:
    return bytes(crypto_rs.pbkdf2_hmac_sha256(
        password.encode("utf-8"), salt, _PBKDF2_ITERS, 32
    ))


def _encode_payload(json_bytes: bytes, key: Optional[bytes]) -> bytes:
    """zlib-compress then optionally AES-GCM-encrypt a JSON payload."""
    compressed = zlib.compress(json_bytes, level=6)
    if key is None:
        return compressed
    return bytes(crypto_rs.weed_encrypt_payload(compressed, key))


def _decode_payload(payload: bytes, key: Optional[bytes]) -> bytes:
    """Reverse of _encode_payload. Raises WeedWrongPassword on auth failure."""
    if key is not None:
        try:
            compressed = crypto_rs.weed_decrypt_payload(payload, key)
        except ValueError as exc:
            raise WeedWrongPassword(str(exc)) from exc
    else:
        compressed = payload
    try:
        return zlib.decompress(compressed)
    except zlib.error as exc:
        raise WeedCorrupted(f"zlib decompression failed: {exc}") from exc


# -- public API ----------------------------------------------------------------

def write_weed(
    path: str | Path,
    gardens_data: List[Dict],
    export_password: Optional[str] = None,
) -> None:
    """Write a .weed export file.

    Args:
        path Destination path (created / overwritten).
        gardens_data List of dicts, each::

                            {
                                "garden": {garden dict including plants array},
                                "events": {plant_id: {events dict}, ...},
                            }

        export_password If supplied every payload is AES-256-GCM encrypted
                        using a PBKDF2 key derived from this password and a
                        fresh random salt stored in the file header.
    """
    flags = FLAG_COMPRESSED
    export_salt = b"\x00" * 16
    key: Optional[bytes] = None

    if export_password:
        flags |= FLAG_ENCRYPTED
        export_salt = os.urandom(16)
        key = _derive_key(export_password, export_salt)

    sections: List[tuple] = [] # (type, uuid_bytes, encoded_payload)

    # MANIFEST section
    garden_ids = [gd["garden"].get("id", "") for gd in gardens_data]
    manifest = {
        "export_date": datetime.now().isoformat(),
        "app_version": APP_VERSION,
        "garden_ids": garden_ids,
        "garden_count": len(garden_ids),
        "events_count": sum(len(gd.get("events", {})) for gd in gardens_data),
    }
    sections.append((
        SECT_MANIFEST,
        b"\x00" * 16,
        _encode_payload(json.dumps(manifest, ensure_ascii=False).encode(), key),
    ))

    # GARDEN + EVENTS sections (one GARDEN section per garden, then its EVENTS)
    for gd in gardens_data:
        garden = gd["garden"]
        gid = garden.get("id", "")
        g_bytes = _uuid_to_bytes(gid)
        sections.append((
            SECT_GARDEN,
            g_bytes,
            _encode_payload(json.dumps(garden, ensure_ascii=False).encode(), key),
        ))
        for plant_id, events in gd.get("events", {}).items():
            sections.append((
                SECT_EVENTS,
                _uuid_to_bytes(plant_id),
                _encode_payload(json.dumps(events, ensure_ascii=False).encode(), key),
            ))

    # Serialise
    buf = bytearray()
    buf += _HDR.pack(WEED_MAGIC, WEED_VERSION, flags, len(sections), export_salt)
    for sect_type, uuid_bytes, payload in sections:
        buf += _SECT.pack(sect_type, uuid_bytes, len(payload))
        buf += payload

    # Integrity footer - HMAC-SHA256 so the footer is authenticated, not just checksummed.
    # For encrypted exports this is redundant (AES-GCM already authenticates every section)
    # but harmless and keeps the footer verification path uniform.
    buf += _hmac.new(_APP_HMAC_KEY, bytes(buf), "sha256").digest()

    Path(path).write_bytes(bytes(buf))


def read_weed(
    path: str | Path,
    export_password: Optional[str] = None,
) -> Dict:
    """Read a .weed file and return its contents.

    Returns a dict::

        {
            "manifest": {manifest dict},
            "gardens": [{garden dict}, ...],
            "events": {plant_id: {events dict}, ...},
            "encrypted": bool,
        }

    Raises:
        WeedCorrupted Bad magic, version, or SHA-256 integrity failure.
        WeedPasswordRequired File is encrypted but no password was given.
        WeedWrongPassword Password given but AES-GCM decryption failed.
    """
    data = Path(path).read_bytes()

    # -- structural minimum size check -------------------------------------
    min_size = _HDR.size + 32
    if len(data) < min_size:
        raise WeedCorrupted("File too small to be a valid .weed file")

    # -- footer integrity check --------------------------------------------
    stored_digest = data[-32:]
    computed = _hmac.new(_APP_HMAC_KEY, data[:-32], "sha256").digest()
    if not _hmac.compare_digest(stored_digest, computed):
        raise WeedCorrupted(
            "Integrity check failed - file is corrupted, truncated, or tampered with"
        )

    # -- header -----------------------------------------------------------
    magic, version, flags, num_sections, export_salt = _HDR.unpack_from(data, 0)
    if magic != WEED_MAGIC:
        raise WeedCorrupted(f"Not a .weed file (bad magic: {magic!r})")
    if version != 0x02:
        raise WeedCorrupted(f"Unsupported .weed version {version}")

    encrypted = bool(flags & FLAG_ENCRYPTED)
    key: Optional[bytes] = None
    if encrypted:
        if not export_password:
            raise WeedPasswordRequired("This .weed file is password-protected")
        key = _derive_key(export_password, export_salt)

    # -- sections ---------------------------------------------------------
    result: Dict = {
        "manifest": None,
        "gardens": [],
        "events": {},
        "encrypted": encrypted,
    }
    offset = _HDR.size
    footer_start = len(data) - 32

    for _ in range(num_sections):
        if offset + _SECT.size > footer_start:
            raise WeedCorrupted("Unexpected end of file while reading section header")

        sect_type, uuid_bytes, payload_len = _SECT.unpack_from(data, offset)
        offset += _SECT.size

        if offset + payload_len > footer_start:
            raise WeedCorrupted("Truncated section payload")

        payload = data[offset: offset + payload_len]
        offset += payload_len

        json_bytes = _decode_payload(payload, key)
        obj = json.loads(json_bytes.decode("utf-8"))

        if sect_type == SECT_MANIFEST:
            result["manifest"] = obj
        elif sect_type == SECT_GARDEN:
            result["gardens"].append(obj)
        elif sect_type == SECT_EVENTS:
            plant_id = obj.get("plant_id") or _bytes_to_uuid(uuid_bytes)
            result["events"][plant_id] = obj

    return result
