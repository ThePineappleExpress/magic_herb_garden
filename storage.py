"""storage.py - Low-level JSON read/write with transparent encryption.

Provides both the legacy flat-file API (load_plants / save_plants) used by
older screens, and the per-garden API (load_garden / save_garden /
load_gardens) used by export/import and the new multi-garden screens.

Atomic writes via .tmp sibling files.  Respects user-configurable db_path
setting for relocating the database.  Encryption is applied automatically
when a CryptoContext key is active.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Base paths (may be overridden at runtime via settings db_path)
# ---------------------------------------------------------------------------
_BASE = Path(os.path.dirname(__file__)) / "usr" / "db"

DB_PATH = _BASE / "plants.json"           # legacy flat plant list
GARDEN_DIR = _BASE / "garden"
EVENTS_DIR = _BASE / "plants"
INDEX_PATH = _BASE / "plants_index.json"
SETTINGS_PATH = _BASE / "settings.json"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dirs():
    """Create data directories if they don't exist."""
    GARDEN_DIR.mkdir(parents=True, exist_ok=True)
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write_json(path: Path, data) -> None:
    """Write *data* as JSON to *path* atomically via a .tmp sibling.

    If a CryptoContext key is active the output bytes are encrypted,
    unless the path is the settings file (always plaintext).
    """
    raw = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")

    # Encrypt unless this is the settings file
    if path.resolve() != SETTINGS_PATH.resolve():
        try:
            from crypto import CryptoContext, encrypt_bytes
            key = CryptoContext.get_key()
            if key is not None:
                aad = path.name.encode("utf-8")
                raw = encrypt_bytes(raw, key, aad=aad)
        except Exception:
            LOG.debug("Encryption unavailable - writing plaintext")

    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp.write_bytes(raw)
        tmp.replace(path)
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except Exception:
            pass
        raise


def _read_json(path: Path):
    """Read and return parsed JSON from *path*.

    Transparently decrypts if the file begins with the ENC1 magic header.
    Returns None if the file does not exist or is empty.
    """
    if not path.exists():
        return None

    raw = path.read_bytes()
    if not raw or not raw.strip():
        return None

    # Transparent decryption
    try:
        from crypto import CryptoContext, decrypt_bytes, is_encrypted
        if is_encrypted(raw):
            key = CryptoContext.get_key()
            if key is None:
                LOG.warning("File %s is encrypted but no key is loaded", path)
                return None
            aad = path.name.encode("utf-8")
            raw = decrypt_bytes(raw, key, aad=aad)
    except ImportError:
        pass  # crypto module not available - treat as plaintext
    except Exception:
        LOG.exception("Failed to decrypt %s", path)
        return None

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        LOG.exception("Failed to parse JSON from %s", path)
        return None


# ---------------------------------------------------------------------------
# Legacy flat-file API (used by garden_view, sow_seed, etc.)
# ---------------------------------------------------------------------------

def _normalize_plants(data):
    """Normalize plant data into a list of dictionaries."""
    if data is None:
        return []
    if isinstance(data, dict):
        return [data]
    if not isinstance(data, list):
        return []

    normalized = []
    for item in data:
        if isinstance(item, dict):
            normalized.append(item)
        elif isinstance(item, list):
            for sub in item:
                if isinstance(sub, dict):
                    normalized.append(sub)
    return normalized


def load_plants():
    """Load plant data from the legacy flat JSON file."""
    data = _read_json(DB_PATH)
    if data is None:
        return []
    return _normalize_plants(data)


def save_plants(plants):
    """Save plant data to the legacy flat JSON file."""
    normalized = _normalize_plants(plants)
    _atomic_write_json(DB_PATH, normalized)


def save_plant(plant):
    """Save a single plant entry to the legacy JSON file and create its events file."""
    plants = load_plants()
    if isinstance(plant, dict):
        plants.append(plant)
    save_plants(plants)

    plant_id = plant.get("id")
    date_planted = plant.get("date_planted", datetime.now().strftime("%Y-%m-%d"))
    initial_event = {
        'id': 'evt-0',
        'ts': date_planted,
        'type': 'planted',
        'volume_l': 0.1,
        'water_temp_c': 18,
        'ph': 5.8,
        'ppm': 140,
        'feeding': {
            'grow_mix': 0.0,
            'root_mix': 0.0,
            'bloom_mix': 0.0,
            'bloom_boost': 0.0,
            'soil_boost': 0.0,
            'vit_boost': 0.0,
            'CalMag': 0.0,
            'myco_trico': False
        },
        'plant': {
            'stage': 'planting',
            'plant_height': 0,
            'num_nodes': 0,
            'node_spacing': 0,
            'main_stem_number': 1,
            'leaf_color': 'light',
            'leaf_morphology': 'normal',
            'deficiencies': {k: False for k in ['n', 'p', 'k', 'ca', 'mg', 's', 'fe', 'mn', 'zn', 'cu', 'b', 'mo']},
            'excess': {k: False for k in ['n', 'p', 'k', 'ca', 'mg', 's', 'fe', 'mn', 'zn', 'cu', 'b', 'mo']}
        },
        'environment': {
            'air_temp_c': 20,
            'rh_percent': 55,
            'soil_moisture': 'wet',
            'soil_ph': 5.5,
            'vpd_kpa': 1.1,
            'ppfd': 100,
            'light_schedule': [18, 6]
        },
        'notes': f"Planted {plant['strain']} from {plant['name']} on {date_planted}."
    }
    events_data = {
        'plant_id': plant_id,
        'penalty': 0,
        'events': [initial_event]
    }
    _ensure_dirs()
    save_plant_events(plant_id, events_data)
    LOG.info("Added plant %s (%s) and created events file.", plant.get('strain'), plant_id)


# ---------------------------------------------------------------------------
# Per-plant events API
# ---------------------------------------------------------------------------

def load_plant_events(plant_id: str):
    """Load events for a single plant by ID."""
    path = EVENTS_DIR / f"{plant_id}.json"
    return _read_json(path)


def save_plant_events(plant_id: str, data) -> bool:
    """Save events data for a single plant. Returns True on success."""
    try:
        _ensure_dirs()
        path = EVENTS_DIR / f"{plant_id}.json"
        _atomic_write_json(path, data)
        return True
    except Exception:
        LOG.exception("Failed to save events for plant %s", plant_id)
        return False


# ---------------------------------------------------------------------------
# Per-garden API (multi-garden support)
# ---------------------------------------------------------------------------

def load_gardens() -> list:
    """Return a list of all garden dicts from usr/db/garden/*.json."""
    if not GARDEN_DIR.exists():
        return []
    gardens = []
    for path in sorted(GARDEN_DIR.glob("*.json")):
        data = _read_json(path)
        if isinstance(data, dict):
            gardens.append(data)
    return gardens


def load_garden(garden_id: str):
    """Load a single garden by its UUID. Returns dict or None."""
    path = GARDEN_DIR / f"{garden_id}.json"
    return _read_json(path)


def save_garden(garden: dict) -> bool:
    """Save a garden dict to usr/db/garden/{id}.json. Returns True on success."""
    gid = garden.get("id")
    if not gid:
        return False
    try:
        _ensure_dirs()
        path = GARDEN_DIR / f"{gid}.json"
        _atomic_write_json(path, garden)
        return True
    except Exception:
        LOG.exception("Failed to save garden %s", gid)
        return False


def delete_garden(garden_id: str) -> bool:
    """Delete a garden file. Returns True on success."""
    path = GARDEN_DIR / f"{garden_id}.json"
    try:
        if path.exists():
            path.unlink()
        return True
    except Exception:
        LOG.exception("Failed to delete garden %s", garden_id)
        return False


# ---------------------------------------------------------------------------
# Settings API (always plaintext)
# ---------------------------------------------------------------------------

def load_settings() -> dict:
    """Load app settings. Always returns a dict (empty if missing)."""
    data = _read_json(SETTINGS_PATH)
    return data if isinstance(data, dict) else {}


def save_settings(settings: dict) -> bool:
    """Save app settings (plaintext). Returns True on success."""
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Settings are always plaintext - write directly
        raw = json.dumps(settings, indent=2, ensure_ascii=False).encode("utf-8")
        tmp = SETTINGS_PATH.with_suffix(SETTINGS_PATH.suffix + ".tmp")
        tmp.write_bytes(raw)
        tmp.replace(SETTINGS_PATH)
        return True
    except Exception:
        LOG.exception("Failed to save settings")
        return False


# ---------------------------------------------------------------------------
# Index API
# ---------------------------------------------------------------------------

def load_index() -> dict:
    """Load the plants index (plant_id → metadata). Returns dict."""
    data = _read_json(INDEX_PATH)
    return data if isinstance(data, dict) else {}


def save_index(index: dict) -> bool:
    """Save the plants index. Returns True on success."""
    try:
        _atomic_write_json(INDEX_PATH, index)
        return True
    except Exception:
        LOG.exception("Failed to save plants index")
        return False
