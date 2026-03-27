"""storage.py - Low-level JSON read/write with transparent encryption.

Resolves the database path at import time:
  1. Check platformdirs location for settings.json
  2. Fall back to local usr/db/settings.json
  3. Honour the ``db_path`` key in settings (user-configurable)

Provides the per-garden API used by the multi-garden architecture.
Plants are stored inside garden files (garden/<uuid>.json → "plants" array).
Per-plant event logs live in plants/<uuid>.json.

Atomic writes via .tmp sibling files.  Encryption is applied automatically
when a CryptoContext key is active.
"""

import json
import logging
import os
from pathlib import Path
from uuid import uuid4

LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(os.path.dirname(__file__))
_LOCAL_DB = _PROJECT_ROOT / "usr" / "db"

def _resolve_db_base() -> Path:
    """Determine the active database directory.

    Order:
      1. platformdirs data dir (``~/.local/share/MagicHerbTracker/db/``)
      2. local ``usr/db/`` fallback

    Within whichever location contains a ``settings.json``, the ``db_path``
    key is honoured if present and the directory exists.
    """
    # Try platformdirs first
    try:
        from platformdirs import user_data_dir
        pd_base = Path(user_data_dir("MagicHerbTracker")) / "db"
    except ImportError:
        pd_base = None

    # Find settings.json
    settings_data = None
    chosen_base = None

    if pd_base and (pd_base / "settings.json").exists():
        chosen_base = pd_base
        try:
            settings_data = json.loads((pd_base / "settings.json").read_bytes())
        except Exception:
            pass
    elif (_LOCAL_DB / "settings.json").exists():
        chosen_base = _LOCAL_DB
        try:
            settings_data = json.loads((_LOCAL_DB / "settings.json").read_bytes())
        except Exception:
            pass

    # Honour db_path from settings
    if isinstance(settings_data, dict) and settings_data.get("db_path"):
        custom = Path(settings_data["db_path"])
        if custom.is_dir():
            return custom

    # Default to whichever base we found, or platformdirs, or local
    if chosen_base:
        return chosen_base
    if pd_base:
        return pd_base
    return _LOCAL_DB


_BASE = _resolve_db_base()

GARDEN_DIR = _BASE / "garden"
EVENTS_DIR = _BASE / "plants"
INDEX_PATH = _BASE / "plants_index.json"
SETTINGS_PATH = _BASE / "settings.json"
PHOTOS_DIR = _BASE / "photos"
PHOTO_INDEX = _BASE / "photos_index.json"

LOG.info("Database path resolved to: %s", _BASE)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ensure_dirs():
    """Create data directories if they don't exist."""
    GARDEN_DIR.mkdir(parents=True, exist_ok=True)
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    PHOTOS_DIR.mkdir(parents=True, exist_ok=True)


def _atomic_write_json(path: Path, data) -> None:
    """Write *data* as JSON to *path* atomically via a .tmp sibling.

    If a CryptoContext key is active the output bytes are encrypted,
    unless the path is the settings file (always plaintext).
    """
    raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode("utf-8")

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
# Per-garden API
# ---------------------------------------------------------------------------

def load_gardens() -> list:
    """Return a list of all garden dicts from garden/*.json."""
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
    """Save a garden dict to garden/{id}.json. Returns True on success."""
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
    """Delete a garden file, all its plants' event files, and all photos."""
    # Collect plant IDs before deleting the garden file
    garden = load_garden(garden_id)
    plant_ids = []
    if isinstance(garden, dict):
        for p in garden.get("plants", []):
            pid = p.get("id")
            if pid:
                plant_ids.append(pid)

    # Delete the garden file
    path = GARDEN_DIR / f"{garden_id}.json"
    try:
        if path.exists():
            path.unlink()
    except Exception:
        LOG.exception("Failed to delete garden file %s", garden_id)
        return False

    # Clean up each plant's events and photos
    for pid in plant_ids:
        # Remove events file
        events_path = EVENTS_DIR / f"{pid}.json"
        try:
            if events_path.exists():
                events_path.unlink()
        except Exception:
            LOG.exception("Failed to delete events for plant %s", pid)
        # Remove photo blobs
        try:
            import photo_storage
            photo_storage.delete_plant_photos(pid)
        except Exception:
            LOG.exception("Failed to delete photo blobs for plant %s", pid)

    # Purge photo index entries for all deleted plants in one pass
    if plant_ids:
        try:
            import photo_storage
            index = photo_storage.load_photo_index()
            plant_id_set = set(plant_ids)
            to_remove = [pid for pid, meta in index.items()
                         if meta.get("plant_id") in plant_id_set]
            if to_remove:
                for pid in to_remove:
                    index.pop(pid, None)
                photo_storage.save_photo_index(index)
            # Invalidate PhotoRepository cache if loaded
            try:
                from data import PhotoRepository
                PhotoRepository.invalidate()
            except ImportError:
                pass
        except Exception:
            LOG.exception("Failed to purge photo index for garden %s", garden_id)

    # Purge plants index entries for all deleted plants
    if plant_ids:
        try:
            plants_index = load_index()
            changed = False
            for pid in plant_ids:
                if pid in plants_index:
                    plants_index.pop(pid)
                    changed = True
            if changed:
                save_index(plants_index)
        except Exception:
            LOG.exception("Failed to purge plants index for garden %s", garden_id)

    return True


# ---------------------------------------------------------------------------
# Plant helpers (plants live inside garden files)
# ---------------------------------------------------------------------------

def get_plants_for_garden(garden_id: str) -> list:
    """Return the plants array from a garden file."""
    garden = load_garden(garden_id)
    if not isinstance(garden, dict):
        return []
    plants = garden.get("plants", [])
    return _normalize_plants(plants)


def _normalize_plants(data) -> list:
    """Filter a plants list to only valid dict entries.

    Returns an empty list for None, non-list, or invalid input.
    """
    if not isinstance(data, list):
        return []
    return [p for p in data if isinstance(p, dict)]


def save_plants_for_garden(garden_id: str, plants: list) -> bool:
    """Replace the plants array in a garden file."""
    garden = load_garden(garden_id)
    if not isinstance(garden, dict):
        return False
    garden["plants"] = plants
    return save_garden(garden)


def add_plant_to_garden(garden_id: str, plant: dict) -> bool:
    """Append a plant dict to a garden's plants array and create its events file."""
    garden = load_garden(garden_id)
    if not isinstance(garden, dict):
        return False
    plants = garden.get("plants", [])
    if not isinstance(plants, list):
        plants = []
    plants.append(plant)
    garden["plants"] = plants
    if not save_garden(garden):
        return False

    # Create initial events file
    plant_id = plant.get("id")
    if plant_id:
        from datetime import datetime
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
            'notes': f"Planted {plant.get('strain', '')} on {date_planted}."
        }
        events_data = {
            'plant_id': plant_id,
            'penalty': 0,
            'events': [initial_event]
        }
        _ensure_dirs()
        save_plant_events(plant_id, events_data)
        LOG.info("Added plant %s (%s) to garden %s", plant.get('strain'), plant_id, garden_id)

    return True


def remove_plant_from_garden(garden_id: str, plant_id: str) -> bool:
    """Remove a plant from a garden's plants array, its events file, and its photos."""
    garden = load_garden(garden_id)
    if not isinstance(garden, dict):
        return False
    plants = garden.get("plants", [])
    garden["plants"] = [p for p in plants if p.get("id") != plant_id]
    if not save_garden(garden):
        return False
    # Remove events file
    events_path = EVENTS_DIR / f"{plant_id}.json"
    try:
        if events_path.exists():
            events_path.unlink()
    except Exception:
        LOG.exception("Failed to delete events file for plant %s", plant_id)
    # Remove photos (blobs + index entries)
    try:
        import photo_storage
        photo_storage.delete_plant_photos(plant_id)
        index = photo_storage.load_photo_index()
        to_remove = [pid for pid, meta in index.items()
                     if meta.get("plant_id") == plant_id]
        if to_remove:
            for pid in to_remove:
                index.pop(pid, None)
            photo_storage.save_photo_index(index)
        # Invalidate PhotoRepository cache if loaded
        try:
            from data import PhotoRepository
            PhotoRepository.invalidate()
        except ImportError:
            pass
    except Exception:
        LOG.exception("Failed to delete photos for plant %s", plant_id)
    # Remove plants index entry
    try:
        plants_index = load_index()
        if plant_id in plants_index:
            plants_index.pop(plant_id)
            save_index(plants_index)
    except Exception:
        LOG.exception("Failed to purge plants index for plant %s", plant_id)
    return True


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
    """Load the plants index (plant_id -> metadata). Returns dict."""
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
