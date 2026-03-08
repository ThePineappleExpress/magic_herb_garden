"""data.py - Repository pattern with in-memory caching.

Four repositories wrapping storage.py:
  - PlantRepository  - per-garden plant CRUD
  - EventRepository  - per-plant events with caching
  - GardenRepository - garden CRUD
  - SettingsRepository - app-wide settings

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
    """Plant CRUD for the legacy flat-file and per-garden plants."""

    _plants_cache = {}  # garden_id -> list of plants

    @classmethod
    def list_for_garden(cls, garden_id: str) -> list:
        """Return plants list for a garden."""
        if garden_id in cls._plants_cache:
            return list(cls._plants_cache[garden_id])
        garden = storage.load_garden(garden_id)
        plants = garden.get("plants", []) if garden else []
        cls._plants_cache[garden_id] = plants
        return list(plants)

    @classmethod
    def list_all_legacy(cls) -> list:
        """Load from the legacy flat plants.json."""
        return storage.load_plants()

    @classmethod
    def save_all_legacy(cls, plants: list):
        """Save to the legacy flat plants.json."""
        storage.save_plants(plants)

    @classmethod
    def add_legacy(cls, plant: dict):
        """Add a plant via the legacy flat-file API."""
        storage.save_plant(plant)

    @classmethod
    def invalidate(cls, garden_id: str = None):
        if garden_id:
            cls._plants_cache.pop(garden_id, None)
        else:
            cls._plants_cache.clear()


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
    def add_event(cls, plant_id: str, event: dict) -> bool:
        """Append an event to a plant's event log and save."""
        data = cls.get(plant_id)
        if data is None:
            data = {"plant_id": plant_id, "penalty": 0, "events": []}
        # Normalize timestamp
        if "ts" not in event:
            event["ts"] = datetime.now().isoformat()
        data["events"].append(event)
        return cls.save(plant_id, data)

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
