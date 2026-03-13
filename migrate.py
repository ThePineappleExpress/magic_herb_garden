"""migrate.py - encrypt/decrypt/re-encrypt all data files in place.

Called from settings_screen when a password is set, changed, or removed.
Never touches settings.json (plaintext by design).
"""

import json
import logging
import shutil
from pathlib import Path

import storage
from crypto import CryptoContext, encrypt_bytes, decrypt_bytes, is_encrypted

LOG = logging.getLogger(__name__)

# Paths that are encrypted when a password is active
_GARDEN_DIR = storage.GARDEN_DIR
_EVENTS_DIR = storage.EVENTS_DIR
_INDEX_PATH = storage.INDEX_PATH
_PHOTOS_DIR = storage.PHOTOS_DIR
_PHOTO_INDEX = storage.PHOTO_INDEX


def _protected_paths():
    """Yield every data path that should be encrypted."""
    if _GARDEN_DIR.exists():
        yield from sorted(_GARDEN_DIR.glob("*.json"))
    if _EVENTS_DIR.exists():
        yield from sorted(_EVENTS_DIR.glob("*.json"))
    if _INDEX_PATH.exists():
        yield _INDEX_PATH
    if _PHOTO_INDEX.exists():
        yield _PHOTO_INDEX
    if _PHOTOS_DIR.exists():
        for plant_dir in sorted(_PHOTOS_DIR.iterdir()):
            if plant_dir.is_dir():
                yield from sorted(plant_dir.glob("*.blob"))


def _atomic_write(path: Path, data: bytes) -> None:
    """Write *data* to *path* atomically via a .tmp sibling."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_bytes(data)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            LOG.warning("Failed to clean up temp file %s", tmp)
        raise


def encrypt_all_data(key: bytes) -> None:
    """Encrypt every plaintext data file in place using *key*.

    Already-encrypted files are skipped (idempotent).
    Writes are atomic: each file is written to a .tmp sibling first,
    then renamed, so a crash cannot leave a file partially written.
    """
    for path in _protected_paths():
        try:
            raw = path.read_bytes()
            if is_encrypted(raw):
                continue # already encrypted - skip
            aad = path.name.encode("utf-8")
            encrypted = encrypt_bytes(raw, key, aad=aad)
            _atomic_write(path, encrypted)
            LOG.info("Encrypted %s", path)
        except Exception:
            LOG.exception("Failed to encrypt %s", path)


def decrypt_all_data(key: bytes) -> None:
    """Decrypt every encrypted data file in place using *key*.

    Plaintext files are skipped (idempotent).
    Writes are atomic: each file is written to a .tmp sibling first,
    then renamed, so a crash cannot leave a file partially written.
    """
    for path in _protected_paths():
        try:
            raw = path.read_bytes()
            if not is_encrypted(raw):
                continue # already plaintext - skip
            aad = path.name.encode("utf-8")
            plaintext = decrypt_bytes(raw, key, aad=aad)
            _atomic_write(path, plaintext)
            LOG.info("Decrypted %s", path)
        except Exception:
            LOG.exception("Failed to decrypt %s", path)


def reencrypt_all_data(old_key: bytes, new_key: bytes) -> None:
    """Re-encrypt every data file from *old_key* to *new_key*.

    File is left unchanged if decryption with old_key fails.
    Writes are atomic: each file is written to a .tmp sibling first,
    then renamed. If the process is killed mid-migration only the
    in-progress file is at risk; all others retain their last state.
    """
    for path in _protected_paths():
        try:
            aad = path.name.encode("utf-8")
            raw = path.read_bytes()
            if is_encrypted(raw):
                plaintext = decrypt_bytes(raw, old_key, aad=aad)
            else:
                plaintext = raw # was plaintext (shouldn't happen, but safe)
            encrypted = encrypt_bytes(plaintext, new_key, aad=aad)
            _atomic_write(path, encrypted)
            LOG.info("Re-encrypted %s", path)
        except ValueError:
            # wrong key / corrupted file - leave untouched and warn
            LOG.warning("Could not re-encrypt %s (decryption failed) - leaving unchanged", path)
        except Exception:
            LOG.exception("Failed to re-encrypt %s", path)


def migrate_db_path(old_base: Path, new_base: Path) -> None:
    """Move all data files from *old_base* to *new_base*.

    Copies each file to the destination then removes the source so that a
    partial failure (e.g. disk-full) leaves the original intact. After a
    successful full migration the old subdirectories are removed if empty.

    Directories moved:
        <base>/garden/*.json
        <base>/plants/*.json
        <base>/plants_index.json
    """
    old_base = Path(old_base).resolve()
    new_base = Path(new_base).resolve()
    if old_base == new_base:
        LOG.info("migrate_db_path: old and new paths are the same - nothing to do")
        return

    for subdir in ("garden", "plants"):
        src_dir = old_base / subdir
        if not src_dir.exists():
            continue
        dst_dir = new_base / subdir
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src_file in sorted(src_dir.glob("*.json")):
            dst_file = dst_dir / src_file.name
            try:
                shutil.copy2(src_file, dst_file)
                src_file.unlink()
                LOG.info("Moved %s → %s", src_file, dst_file)
            except Exception:
                LOG.exception("Failed to move %s to %s", src_file, dst_file)

    for idx_name in ("plants_index.json", "photos_index.json"):
        src_index = old_base / idx_name
        if src_index.exists():
            new_base.mkdir(parents=True, exist_ok=True)
            dst_index = new_base / idx_name
            try:
                shutil.copy2(src_index, dst_index)
                src_index.unlink()
                LOG.info("Moved index %s → %s", src_index, dst_index)
            except Exception:
                LOG.exception("Failed to move index %s to %s", src_index, dst_index)

    # Move photos directory
    src_photos = old_base / "photos"
    if src_photos.exists():
        dst_photos = new_base / "photos"
        try:
            shutil.copytree(src_photos, dst_photos, dirs_exist_ok=True)
            shutil.rmtree(src_photos)
            LOG.info("Moved photos %s → %s", src_photos, dst_photos)
        except Exception:
            LOG.exception("Failed to move photos %s to %s", src_photos, dst_photos)

    # Clean up now-empty old subdirectories (best-effort)
    for subdir in ("garden", "plants", "photos"):
        old_sub = old_base / subdir
        try:
            if old_sub.exists() and not any(old_sub.iterdir()):
                old_sub.rmdir()
        except Exception:
            LOG.warning("Failed to remove empty directory %s", old_sub)
