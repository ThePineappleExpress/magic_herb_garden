"""Tests for migrate.py - encrypt/decrypt/reencrypt/migrate_db_path.

Uses tempfile for isolated test directories with real files.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

from crypto import encrypt_bytes, decrypt_bytes, is_encrypted
import migrate


def _make_tmp_db():
    """Create a temp dir with garden and plants subdirs populated with test data."""
    tmp = Path(tempfile.mkdtemp(prefix="mht_migrate_test_"))
    garden_dir = tmp / "garden"
    plants_dir = tmp / "plants"
    garden_dir.mkdir()
    plants_dir.mkdir()

    # Create some test JSON files
    g1 = {"id": "g1", "name": "Garden A", "plants": []}
    (garden_dir / "g1.json").write_bytes(json.dumps(g1).encode())

    e1 = {"plant_id": "p1", "events": [{"id": "e1", "ts": "2025-01-01", "type": "log"}]}
    (plants_dir / "p1.json").write_bytes(json.dumps(e1).encode())

    idx = {"p1": {"last_event_ts": "2025-01-01", "events_count": 1}}
    (tmp / "plants_index.json").write_bytes(json.dumps(idx).encode())

    return tmp


def _patch_migrate_paths(tmp):
    """Point migrate module's paths at the temp directory."""
    migrate._GARDEN_DIR = tmp / "garden"
    migrate._EVENTS_DIR = tmp / "plants"
    migrate._INDEX_PATH = tmp / "plants_index.json"
    migrate._PHOTOS_DIR = tmp / "photos"
    migrate._PHOTO_INDEX = tmp / "photos_index.json"


def _restore_migrate_paths():
    """Restore original migrate paths."""
    import storage
    migrate._GARDEN_DIR = storage.GARDEN_DIR
    migrate._EVENTS_DIR = storage.EVENTS_DIR
    migrate._INDEX_PATH = storage.INDEX_PATH
    migrate._PHOTOS_DIR = storage.PHOTOS_DIR
    migrate._PHOTO_INDEX = storage.PHOTO_INDEX


def _make_key():
    """Generate a 32-byte test encryption key."""
    return os.urandom(32)


# ---------------------------------------------------------------------------
# encrypt_all_data
# ---------------------------------------------------------------------------

def test_encrypt_all_data():
    tmp = _make_tmp_db()
    _patch_migrate_paths(tmp)
    try:
        key = _make_key()
        migrate.encrypt_all_data(key)

        # All JSON files should now be encrypted
        garden_file = tmp / "garden" / "g1.json"
        raw = garden_file.read_bytes()
        assert is_encrypted(raw), "Garden file should be encrypted"

        events_file = tmp / "plants" / "p1.json"
        raw = events_file.read_bytes()
        assert is_encrypted(raw), "Events file should be encrypted"

        index_file = tmp / "plants_index.json"
        raw = index_file.read_bytes()
        assert is_encrypted(raw), "Index file should be encrypted"
    finally:
        _restore_migrate_paths()
        shutil.rmtree(tmp)


def test_encrypt_idempotent():
    tmp = _make_tmp_db()
    _patch_migrate_paths(tmp)
    try:
        key = _make_key()
        migrate.encrypt_all_data(key)
        # Encrypt again - should be a no-op (already encrypted)
        migrate.encrypt_all_data(key)

        garden_file = tmp / "garden" / "g1.json"
        raw = garden_file.read_bytes()
        assert is_encrypted(raw), "Should still be encrypted"
        # Should still be decryptable with same key
        aad = garden_file.name.encode("utf-8")
        plaintext = decrypt_bytes(raw, key, aad=aad)
        data = json.loads(plaintext)
        assert data["id"] == "g1"
    finally:
        _restore_migrate_paths()
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# decrypt_all_data
# ---------------------------------------------------------------------------

def test_decrypt_all_data():
    tmp = _make_tmp_db()
    _patch_migrate_paths(tmp)
    try:
        key = _make_key()
        migrate.encrypt_all_data(key)

        # Now decrypt
        migrate.decrypt_all_data(key)

        garden_file = tmp / "garden" / "g1.json"
        raw = garden_file.read_bytes()
        assert not is_encrypted(raw), "Garden file should be plaintext"
        data = json.loads(raw)
        assert data["id"] == "g1"
    finally:
        _restore_migrate_paths()
        shutil.rmtree(tmp)


def test_decrypt_idempotent():
    tmp = _make_tmp_db()
    _patch_migrate_paths(tmp)
    try:
        key = _make_key()
        # Files start as plaintext - decrypt should be a no-op
        migrate.decrypt_all_data(key)

        garden_file = tmp / "garden" / "g1.json"
        raw = garden_file.read_bytes()
        data = json.loads(raw)
        assert data["id"] == "g1"
    finally:
        _restore_migrate_paths()
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# reencrypt_all_data
# ---------------------------------------------------------------------------

def test_reencrypt_all_data():
    tmp = _make_tmp_db()
    _patch_migrate_paths(tmp)
    try:
        old_key = _make_key()
        new_key = _make_key()
        migrate.encrypt_all_data(old_key)

        # Re-encrypt with new key
        migrate.reencrypt_all_data(old_key, new_key)

        garden_file = tmp / "garden" / "g1.json"
        raw = garden_file.read_bytes()
        assert is_encrypted(raw), "Should still be encrypted"

        # Should be decryptable with new key
        aad = garden_file.name.encode("utf-8")
        plaintext = decrypt_bytes(raw, new_key, aad=aad)
        data = json.loads(plaintext)
        assert data["id"] == "g1"

        # Should NOT be decryptable with old key
        try:
            decrypt_bytes(raw, old_key, aad=aad)
            assert False, "Old key should not decrypt"
        except (ValueError, Exception):
            pass
    finally:
        _restore_migrate_paths()
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# migrate_db_path
# ---------------------------------------------------------------------------

def test_migrate_db_path():
    tmp = _make_tmp_db()
    new_base = Path(tempfile.mkdtemp(prefix="mht_migrate_new_"))
    try:
        migrate.migrate_db_path(tmp, new_base)

        # Files should exist in new location
        assert (new_base / "garden" / "g1.json").exists()
        assert (new_base / "plants" / "p1.json").exists()
        assert (new_base / "plants_index.json").exists()

        # Files should NOT exist in old location
        assert not (tmp / "garden" / "g1.json").exists()
        assert not (tmp / "plants" / "p1.json").exists()
        assert not (tmp / "plants_index.json").exists()

        # Data should be intact
        data = json.loads((new_base / "garden" / "g1.json").read_bytes())
        assert data["id"] == "g1"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.rmtree(new_base, ignore_errors=True)


def test_migrate_db_path_same_path_noop():
    tmp = _make_tmp_db()
    try:
        # Should not raise and do nothing
        migrate.migrate_db_path(tmp, tmp)
        # Files should still be there
        assert (tmp / "garden" / "g1.json").exists()
    finally:
        shutil.rmtree(tmp)


def test_migrate_db_path_missing_source():
    """Source dirs that don't exist are simply skipped."""
    src = Path(tempfile.mkdtemp(prefix="mht_migrate_empty_"))
    dst = Path(tempfile.mkdtemp(prefix="mht_migrate_dst_"))
    try:
        # Source has no garden/plants subdirs - should not raise
        migrate.migrate_db_path(src, dst)
    finally:
        shutil.rmtree(src, ignore_errors=True)
        shutil.rmtree(dst, ignore_errors=True)
