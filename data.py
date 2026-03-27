"""data.py - Repository pattern with in-memory caching.

Five repositories wrapping storage.py:
  - PlantRepository  - per-garden plant CRUD
  - EventRepository  - per-plant events with caching
  - GardenRepository - garden CRUD
  - SettingsRepository - app-wide settings
  - PhotoRepository  - photo CRUD with cached index

Always access data through these repositories, not storage.py directly.
"""

import logging
from datetime import datetime

import storage

LOG = logging.getLogger(__name__)


class GardenRepository:
    """Garden CRUD with a simple in-memory cache."""

    _gardens_cache = None  # list or None

    @classmethod
    def list_all(cls) -> list:
        if cls._gardens_cache is None:
            cls._gardens_cache = storage.load_gardens()
        return list(cls._gardens_cache)

    @classmethod
    def get(cls, garden_id: str):
        """Return a single garden dict, or None."""
        # Check cache first
        if cls._gardens_cache is not None:
            for g in cls._gardens_cache:
                if g.get("id") == garden_id:
                    return g
        return storage.load_garden(garden_id)

    @classmethod
    def save(cls, garden: dict) -> bool:
        ok = storage.save_garden(garden)
        if ok:
            cls._gardens_cache = None  # invalidate
        return ok

    @classmethod
    def delete(cls, garden_id: str) -> bool:
        ok = storage.delete_garden(garden_id)
        if ok:
            cls._gardens_cache = None
        return ok

    @classmethod
    def invalidate(cls):
        cls._gardens_cache = None


class PlantRepository:
    """Plant CRUD via per-garden storage."""

    _plants_cache = {}  # garden_id -> list of plants

    @classmethod
    def list_for_garden(cls, garden_id: str) -> list:
        """Return plants list for a garden."""
        if garden_id in cls._plants_cache:
            return list(cls._plants_cache[garden_id])
        plants = storage.get_plants_for_garden(garden_id)
        cls._plants_cache[garden_id] = plants
        return list(plants)

    @classmethod
    def get(cls, garden_id: str, plant_id: str):
        """Return a single plant dict from *garden_id*, or None."""
        plants = cls.list_for_garden(garden_id)
        for p in plants:
            if isinstance(p, dict) and p.get("id") == plant_id:
                return dict(p)
        return None

    @classmethod
    def add(cls, garden_id: str, plant: dict) -> bool:
        """Add a plant to a garden."""
        ok = storage.add_plant_to_garden(garden_id, plant)
        if ok:
            cls._plants_cache.pop(garden_id, None)
        return ok

    @classmethod
    def remove(cls, garden_id: str, plant_id: str) -> bool:
        """Remove a plant from a garden."""
        ok = storage.remove_plant_from_garden(garden_id, plant_id)
        if ok:
            cls._plants_cache.pop(garden_id, None)
        return ok

    @classmethod
    def update(cls, garden_id: str, plant_id: str, plant_dict: dict) -> bool:
        """Replace the plant with *plant_id* in *garden_id* with *plant_dict*.

        The plant's ``id`` field is preserved/forced to *plant_id*.
        Returns False if the garden or plant is not found.
        """
        garden = storage.load_garden(garden_id)
        if not isinstance(garden, dict):
            return False
        plants = garden.get("plants", [])
        found = False
        for i, p in enumerate(plants):
            if isinstance(p, dict) and p.get("id") == plant_id:
                plant_dict["id"] = plant_id
                plants[i] = plant_dict
                found = True
                break
        if not found:
            return False
        garden["plants"] = plants
        ok = storage.save_garden(garden)
        if ok:
            cls._plants_cache.pop(garden_id, None)
        return ok

    @classmethod
    def update_field(cls, garden_id: str, plant_id: str, key: str, value) -> bool:
        """Update a single field on a plant without replacing the whole dict.

        Convenience wrapper around :meth:`update` that reads the current
        plant, sets *key* to *value*, and writes it back.
        Returns False if the plant is not found.
        """
        plant = cls.get(garden_id, plant_id)
        if plant is None:
            return False
        plant[key] = value
        return cls.update(garden_id, plant_id, plant)

    @classmethod
    def invalidate(cls, garden_id: str = None):
        if garden_id:
            cls._plants_cache.pop(garden_id, None)
        else:
            cls._plants_cache.clear()


class IndexRepository:
    """Plants-index CRUD with in-memory caching.

    Wraps ``storage.load_index()`` / ``storage.save_index()`` to provide
    a single cached access point for the lightweight plant metadata index.
    """

    _cache: dict | None = None

    @classmethod
    def get_all(cls) -> dict:
        """Return the full index dict (plant_id -> metadata)."""
        if cls._cache is None:
            cls._cache = storage.load_index()
        return dict(cls._cache)

    @classmethod
    def get(cls, plant_id: str) -> dict | None:
        """Return index entry for a single plant, or None."""
        return cls.get_all().get(plant_id)

    @classmethod
    def set(cls, plant_id: str, entry: dict) -> bool:
        """Set or update the index entry for *plant_id* and save."""
        index = cls.get_all()
        index[plant_id] = entry
        ok = storage.save_index(index)
        if ok:
            cls._cache = index
        return ok

    @classmethod
    def remove(cls, plant_id: str) -> bool:
        """Remove an entry from the index and save."""
        index = cls.get_all()
        if plant_id not in index:
            return True  # nothing to remove
        index.pop(plant_id)
        ok = storage.save_index(index)
        if ok:
            cls._cache = index
        return ok

    @classmethod
    def invalidate(cls):
        cls._cache = None


class EventRepository:
    """Per-plant event CRUD with caching."""

    _cache = {}  # plant_id -> events dict

    @classmethod
    def get(cls, plant_id: str):
        """Return the events dict for a plant (includes 'events' list)."""
        if plant_id in cls._cache:
            return cls._cache[plant_id]
        data = storage.load_plant_events(plant_id)
        if data:
            cls._cache[plant_id] = data
        return data

    @classmethod
    def save(cls, plant_id: str, data: dict) -> bool:
        ok = storage.save_plant_events(plant_id, data)
        if ok:
            cls._cache[plant_id] = data
        return ok

    @classmethod
    def _update_plants_index(cls, plant_id: str, data: dict):
        """Update plants_index.json with latest event metadata."""
        try:
            index = storage.load_index()
            events = data.get("events", [])
            if events:
                # Find the latest timestamp across all events
                latest_ts = max(
                    (ev.get("ts", "") for ev in events if isinstance(ev, dict)),
                    default=""
                )
                index[plant_id] = {
                    "last_event_ts": latest_ts,
                    "events_count": len(events),
                }
            else:
                index.pop(plant_id, None)
            storage.save_index(index)
        except Exception:
            LOG.exception("Failed to update plants index for %s", plant_id)

    @classmethod
    def add_event(cls, plant_id: str, event: dict) -> bool:
        """Append an event to a plant's event log and save."""
        data = cls.get(plant_id)
        if data is None:
            data = {"plant_id": plant_id, "penalty": 0, "events": []}
        # Normalize timestamp
        if "ts" not in event:
            event["ts"] = datetime.now().isoformat()
        data["events"].append(event)
        ok = cls.save(plant_id, data)
        if ok:
            cls._update_plants_index(plant_id, data)
        return ok

    @classmethod
    def update_event(cls, plant_id: str, event_id: str, updated_event: dict) -> bool:
        """Replace an existing event (by id) with updated data and save."""
        data = cls.get(plant_id)
        if data is None:
            return False
        events = data.get("events", [])
        for i, ev in enumerate(events):
            if isinstance(ev, dict) and ev.get("id") == event_id:
                # Preserve original id and timestamp
                updated_event["id"] = event_id
                if "ts" not in updated_event:
                    updated_event["ts"] = ev.get("ts", datetime.now().isoformat())
                events[i] = updated_event
                data["events"] = events
                ok = cls.save(plant_id, data)
                if ok:
                    cls._update_plants_index(plant_id, data)
                return ok
        return False

    @classmethod
    def invalidate(cls, plant_id: str = None):
        if plant_id:
            cls._cache.pop(plant_id, None)
        else:
            cls._cache.clear()


class SettingsRepository:
    """App-wide settings (always plaintext on disk)."""

    _cache = None

    @classmethod
    def get_all(cls) -> dict:
        if cls._cache is None:
            cls._cache = storage.load_settings()
        return dict(cls._cache)

    @classmethod
    def get(cls, key: str, default=None):
        settings = cls.get_all()
        return settings.get(key, default)

    @classmethod
    def set(cls, key: str, value) -> bool:
        settings = cls.get_all()
        settings[key] = value
        ok = storage.save_settings(settings)
        if ok:
            cls._cache = settings
        return ok

    @classmethod
    def save_all(cls, settings: dict) -> bool:
        ok = storage.save_settings(settings)
        if ok:
            cls._cache = settings
        return ok

    @classmethod
    def invalidate(cls):
        cls._cache = None


class PhotoRepository:
    """Photo CRUD with cached index."""

    _index_cache: dict | None = None

    @classmethod
    def _load_index(cls) -> dict:
        if cls._index_cache is None:
            import photo_storage
            cls._index_cache = photo_storage.load_photo_index()
        return cls._index_cache

    @classmethod
    def attach(cls, plant_id: str, event_id: str, garden_id: str,
               photo_id: str, image_bytes: bytes, original_name: str) -> bool:
        """Full attach flow: validate, thumbnail, save blobs, update index.

        Uses process_image() for single-decode: one Image.open() call for
        validation + metadata + thumbnail instead of four.
        """
        from photo_utils import process_image
        import photo_storage

        result = process_image(image_bytes)
        if result is None:
            LOG.warning("Invalid image rejected: %s", original_name)
            return False

        if not photo_storage.save_photo(plant_id, photo_id, image_bytes):
            return False
        if not photo_storage.save_thumbnail(plant_id, photo_id, result["thumb_bytes"]):
            return False

        index = cls._load_index()
        index[photo_id] = {
            "plant_id": plant_id,
            "event_id": event_id,
            "garden_id": garden_id,
            "original_name": original_name,
            "mime": result["mime"],
            "width": result["width"],
            "height": result["height"],
            "thumb_width": result["thumb_width"],
            "thumb_height": result["thumb_height"],
            "size_bytes": len(image_bytes),
            "added_ts": datetime.now().isoformat(),
        }
        if not photo_storage.save_photo_index(index):
            return False
        cls._index_cache = index
        return True

    @classmethod
    def detach(cls, plant_id: str, photo_id: str) -> bool:
        """Delete blob + thumb, remove from index, save index."""
        import photo_storage
        photo_storage.delete_photo(plant_id, photo_id)
        index = cls._load_index()
        index.pop(photo_id, None)
        ok = photo_storage.save_photo_index(index)
        if ok:
            cls._index_cache = index
        return ok

    @classmethod
    def detach_all_for_event(cls, plant_id: str, event_id: str) -> bool:
        """Remove all photos linked to an event."""
        import photo_storage
        index = cls._load_index()
        to_remove = [pid for pid, meta in index.items()
                     if meta.get("event_id") == event_id]
        for pid in to_remove:
            photo_storage.delete_photo(plant_id, pid)
            index.pop(pid, None)
        ok = photo_storage.save_photo_index(index)
        if ok:
            cls._index_cache = index
        return ok

    @classmethod
    def detach_all_for_plant(cls, plant_id: str) -> bool:
        """Bulk delete: rmtree + purge index entries."""
        import photo_storage
        photo_storage.delete_plant_photos(plant_id)
        index = cls._load_index()
        to_remove = [pid for pid, meta in index.items()
                     if meta.get("plant_id") == plant_id]
        for pid in to_remove:
            index.pop(pid, None)
        ok = photo_storage.save_photo_index(index)
        if ok:
            cls._index_cache = index
        return ok

    @classmethod
    def get_meta(cls, photo_id: str) -> dict | None:
        """Return index entry for a single photo."""
        return cls._load_index().get(photo_id)

    @classmethod
    def list_for_event(cls, event_id: str, plant_id: str = "") -> list[dict]:
        """Return index entries where event_id matches.

        If *plant_id* is provided, results are also filtered by plant_id
        to prevent cross-plant photo leakage when event IDs collide.
        """
        index = cls._load_index()
        results = []
        for pid, meta in index.items():
            if meta.get("event_id") != event_id:
                continue
            if plant_id and meta.get("plant_id") != plant_id:
                continue
            results.append({"id": pid, **meta})
        return results

    @classmethod
    def list_for_plant(cls, plant_id: str) -> list[dict]:
        """Return index entries where plant_id matches."""
        index = cls._load_index()
        return [{"id": pid, **meta} for pid, meta in index.items()
                if meta.get("plant_id") == plant_id]

    @classmethod
    def load_photo_bytes(cls, plant_id: str, photo_id: str) -> bytes | None:
        import photo_storage
        return photo_storage.load_photo(plant_id, photo_id)

    @classmethod
    def load_thumb_bytes(cls, plant_id: str, photo_id: str) -> bytes | None:
        import photo_storage
        return photo_storage.load_thumbnail(plant_id, photo_id)

    @classmethod
    def invalidate(cls):
        cls._index_cache = None
