"""photo_storage.py - Low-level binary blob I/O for photo attachments.

Mirrors storage.py patterns: atomic writes via .tmp sibling, transparent
encryption via CryptoContext, graceful fallback on missing/corrupt files.
"""

import json
import logging
import shutil
from pathlib import Path

LOG = logging.getLogger(__name__)

# Resolve base from storage module to stay consistent
from storage import _BASE

PHOTOS_DIR = _BASE / "photos"
PHOTO_INDEX = _BASE / "photos_index.json"


def _ensure_photo_dirs():
    """Create the top-level photos directory if needed."""
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_plant_photo_dir(plant_id: str) -> Path:
    """Create and return photos/{plant_id}/ directory."""
    d = PHOTOS_DIR / str(plant_id)
    d.mkdir(parents=True, exist_ok=True)
    return d


def _atomic_write_blob(path: Path, data: bytes) -> None:
    """Write raw bytes atomically. Encrypts if CryptoContext key is active."""
    try:
        from crypto import CryptoContext, encrypt_bytes
        key = CryptoContext.get_key()
        if key is not None:
            aad = path.name.encode("utf-8")
            data = encrypt_bytes(data, key, aad=aad)
    except Exception:
        LOG.debug("Encryption unavailable - writing plaintext blob")

    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(data)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def _read_blob(path: Path) -> bytes | None:
    """Read bytes, transparently decrypt if ENC1 header detected."""
    if not path.exists():
        return None
    try:
        raw = path.read_bytes()
        if not raw:
            return None
        try:
            from crypto import CryptoContext, is_encrypted, decrypt_bytes
            if is_encrypted(raw):
                key = CryptoContext.get_key()
                if key is None:
                    LOG.warning("Encrypted blob but no key loaded: %s", path)
                    return None
                aad = path.name.encode("utf-8")
                raw = decrypt_bytes(raw, key, aad=aad)
        except ImportError:
            pass
        return raw
    except Exception:
        LOG.exception("Failed to read blob: %s", path)
        return None


# -- Public API: photo blobs ------------------------------------------------

def save_photo(plant_id: str, photo_id: str, image_bytes: bytes) -> bool:
    """Write full-size blob to photos/{plant_id}/{photo_id}.blob."""
    try:
        d = _ensure_plant_photo_dir(plant_id)
        _atomic_write_blob(d / f"{photo_id}.blob", image_bytes)
        return True
    except Exception:
        LOG.exception("Failed to save photo %s for plant %s", photo_id, plant_id)
        return False


def save_thumbnail(plant_id: str, photo_id: str, thumb_bytes: bytes) -> bool:
    """Write thumbnail to photos/{plant_id}/{photo_id}.thumb.blob."""
    try:
        d = _ensure_plant_photo_dir(plant_id)
        _atomic_write_blob(d / f"{photo_id}.thumb.blob", thumb_bytes)
        return True
    except Exception:
        LOG.exception("Failed to save thumbnail %s for plant %s", photo_id, plant_id)
        return False


def load_photo(plant_id: str, photo_id: str) -> bytes | None:
    """Read and decrypt the full-size blob. Returns None on missing/error."""
    return _read_blob(PHOTOS_DIR / str(plant_id) / f"{photo_id}.blob")


def load_thumbnail(plant_id: str, photo_id: str) -> bytes | None:
    """Read and decrypt the thumbnail blob."""
    return _read_blob(PHOTOS_DIR / str(plant_id) / f"{photo_id}.thumb.blob")


def delete_photo(plant_id: str, photo_id: str) -> bool:
    """Delete both .blob and .thumb.blob for a photo."""
    try:
        base = PHOTOS_DIR / str(plant_id)
        for suffix in (".blob", ".thumb.blob"):
            p = base / f"{photo_id}{suffix}"
            if p.exists():
                p.unlink()
        return True
    except Exception:
        LOG.exception("Failed to delete photo %s for plant %s", photo_id, plant_id)
        return False


def delete_plant_photos(plant_id: str) -> bool:
    """Remove the entire photos/{plant_id}/ directory."""
    try:
        d = PHOTOS_DIR / str(plant_id)
        if d.exists():
            shutil.rmtree(d)
        return True
    except Exception:
        LOG.exception("Failed to delete photos for plant %s", plant_id)
        return False


def list_photo_files(plant_id: str) -> list[str]:
    """Return photo_id list from photos/{plant_id}/*.blob (exclude thumbs)."""
    d = PHOTOS_DIR / str(plant_id)
    if not d.exists():
        return []
    result = []
    for p in sorted(d.glob("*.blob")):
        name = p.stem
        if not name.endswith(".thumb"):
            result.append(name)
    return result


# -- Public API: photo index ------------------------------------------------

def load_photo_index() -> dict:
    """Read photos_index.json (transparent decrypt). Returns {} on missing."""
    if not PHOTO_INDEX.exists():
        return {}
    try:
        raw = PHOTO_INDEX.read_bytes()
        if not raw:
            return {}
        try:
            from crypto import CryptoContext, is_encrypted, decrypt_bytes
            if is_encrypted(raw):
                key = CryptoContext.get_key()
                if key is None:
                    LOG.warning("Encrypted photo index but no key loaded")
                    return {}
                aad = PHOTO_INDEX.name.encode("utf-8")
                raw = decrypt_bytes(raw, key, aad=aad)
        except ImportError:
            pass
        return json.loads(raw)
    except Exception:
        LOG.exception("Failed to load photo index")
        return {}


def save_photo_index(index: dict) -> bool:
    """Atomic-write photos_index.json (transparent encrypt)."""
    try:
        raw = json.dumps(index, indent=2, ensure_ascii=False).encode("utf-8")
        try:
            from crypto import CryptoContext, encrypt_bytes
            key = CryptoContext.get_key()
            if key is not None:
                aad = PHOTO_INDEX.name.encode("utf-8")
                raw = encrypt_bytes(raw, key, aad=aad)
        except Exception:
            LOG.debug("Encryption unavailable - writing plaintext index")

        tmp = PHOTO_INDEX.with_suffix(".json.tmp")
        PHOTO_INDEX.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(raw)
        tmp.replace(PHOTO_INDEX)
        return True
    except Exception:
        LOG.exception("Failed to save photo index")
        return False