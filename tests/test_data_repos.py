"""Tests for repository methods added in Phase 0.

Covers:
  - PlantRepository.get / update / update_field
  - IndexRepository  CRUD + caching
  - validators.check_plant / check_event / check_garden  (error-list API)

All storage I/O is monkey-patched on the data module so no disk access
is needed and no sys.modules pollution occurs.
"""

import copy

import data as _data_mod  # import the module object so we can patch its storage ref
from data import (
    GardenRepository,
    PlantRepository,
    EventRepository,
    IndexRepository,
    SettingsRepository,
)
import validators

# ---------------------------------------------------------------------------
# In-memory fake backing stores
# ---------------------------------------------------------------------------

_fake_gardens: dict = {}
_fake_events: dict = {}
_fake_index: dict = {}

_real_storage = _data_mod.storage  # save the real reference


class _FakeStorage:
    """Drop-in replacement for storage, backed by module-level dicts."""

    @staticmethod
    def load_garden(gid):
        g = _fake_gardens.get(gid)
        return copy.deepcopy(g) if g else None

    @staticmethod
    def load_gardens():
        return [copy.deepcopy(g) for g in _fake_gardens.values()]

    @staticmethod
    def save_garden(garden):
        gid = garden.get("id")
        if not gid:
            return False
        _fake_gardens[gid] = copy.deepcopy(garden)
        return True

    @staticmethod
    def delete_garden(gid):
        _fake_gardens.pop(gid, None)
        return True

    @staticmethod
    def get_plants_for_garden(gid):
        g = _fake_gardens.get(gid)
        if not g:
            return []
        return [p for p in g.get("plants", []) if isinstance(p, dict)]

    @staticmethod
    def add_plant_to_garden(gid, plant):
        g = _fake_gardens.get(gid)
        if not g:
            return False
        g.setdefault("plants", []).append(copy.deepcopy(plant))
        return True

    @staticmethod
    def remove_plant_from_garden(gid, pid):
        g = _fake_gardens.get(gid)
        if not g:
            return False
        g["plants"] = [p for p in g.get("plants", []) if p.get("id") != pid]
        return True

    @staticmethod
    def load_plant_events(pid):
        d = _fake_events.get(pid)
        return copy.deepcopy(d) if d else None

    @staticmethod
    def save_plant_events(pid, d):
        _fake_events[pid] = copy.deepcopy(d)
        return True

    @staticmethod
    def load_index():
        return copy.deepcopy(_fake_index)

    @staticmethod
    def save_index(index):
        global _fake_index
        _fake_index = copy.deepcopy(index)
        return True

    @staticmethod
    def load_settings():
        return {}

    @staticmethod
    def save_settings(s):
        return True


# Patch data module's storage reference
_data_mod.storage = _FakeStorage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup():
    """Reset all fakes and caches before each test."""
    global _fake_gardens, _fake_events, _fake_index
    _fake_gardens = {}
    _fake_events = {}
    _fake_index = {}
    GardenRepository.invalidate()
    PlantRepository.invalidate()
    EventRepository.invalidate()
    IndexRepository.invalidate()
    SettingsRepository.invalidate()


def _seed_garden(garden_id="g1", plants=None):
    """Insert a garden with optional plants into the fake store."""
    _fake_gardens[garden_id] = {
        "id": garden_id,
        "name": "Test Garden",
        "plants": plants or [],
    }


def _make_plant(pid="p1", strain="Northern Lights"):
    return {"id": pid, "strain": strain, "status": "veg"}


# ===================================================================
# PlantRepository.get
# ===================================================================

def test_plant_repo_get_returns_plant():
    _setup()
    plant = _make_plant("p1")
    _seed_garden("g1", [plant])
    result = PlantRepository.get("g1", "p1")
    assert result is not None
    assert result["id"] == "p1"
    assert result["strain"] == "Northern Lights"


def test_plant_repo_get_returns_none_for_missing_plant():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    assert PlantRepository.get("g1", "p999") is None


def test_plant_repo_get_returns_none_for_missing_garden():
    _setup()
    assert PlantRepository.get("g999", "p1") is None


def test_plant_repo_get_returns_copy():
    """Returned dict should be a copy, not a reference to cached data."""
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    a = PlantRepository.get("g1", "p1")
    b = PlantRepository.get("g1", "p1")
    assert a == b
    a["strain"] = "MUTATED"
    b2 = PlantRepository.get("g1", "p1")
    assert b2["strain"] == "Northern Lights"


# ===================================================================
# PlantRepository.update
# ===================================================================

def test_plant_repo_update_replaces_plant():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    updated = {"id": "p1", "strain": "Blue Dream", "status": "flower"}
    assert PlantRepository.update("g1", "p1", updated) is True
    got = PlantRepository.get("g1", "p1")
    assert got["strain"] == "Blue Dream"
    assert got["status"] == "flower"


def test_plant_repo_update_preserves_other_plants():
    _setup()
    _seed_garden("g1", [_make_plant("p1"), _make_plant("p2", "Haze")])
    PlantRepository.update("g1", "p1", {"strain": "New Strain"})
    p2 = PlantRepository.get("g1", "p2")
    assert p2["strain"] == "Haze"


def test_plant_repo_update_forces_id():
    """update() must force the plant_id to match, even if caller provides a different id."""
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    PlantRepository.update("g1", "p1", {"id": "WRONG", "strain": "X"})
    got = PlantRepository.get("g1", "p1")
    assert got["id"] == "p1"


def test_plant_repo_update_missing_plant_returns_false():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    assert PlantRepository.update("g1", "p999", {"strain": "X"}) is False


def test_plant_repo_update_missing_garden_returns_false():
    _setup()
    assert PlantRepository.update("g999", "p1", {"strain": "X"}) is False


# ===================================================================
# PlantRepository.update_field
# ===================================================================

def test_plant_repo_update_field():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    assert PlantRepository.update_field("g1", "p1", "status", "flower") is True
    got = PlantRepository.get("g1", "p1")
    assert got["status"] == "flower"
    # Other fields unchanged
    assert got["strain"] == "Northern Lights"


def test_plant_repo_update_field_adds_new_key():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    PlantRepository.update_field("g1", "p1", "notes", "Looking great")
    got = PlantRepository.get("g1", "p1")
    assert got["notes"] == "Looking great"


def test_plant_repo_update_field_missing_plant():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    assert PlantRepository.update_field("g1", "p999", "status", "dead") is False


# ===================================================================
# IndexRepository
# ===================================================================

def test_index_repo_empty():
    _setup()
    assert IndexRepository.get_all() == {}


def test_index_repo_set_and_get():
    _setup()
    IndexRepository.set("p1", {"last_event_ts": "2025-01-01", "events_count": 3})
    entry = IndexRepository.get("p1")
    assert entry is not None
    assert entry["events_count"] == 3


def test_index_repo_get_none_for_missing():
    _setup()
    assert IndexRepository.get("p999") is None


def test_index_repo_remove():
    _setup()
    IndexRepository.set("p1", {"last_event_ts": "2025-01-01", "events_count": 1})
    assert IndexRepository.remove("p1") is True
    assert IndexRepository.get("p1") is None


def test_index_repo_remove_missing_is_noop():
    _setup()
    assert IndexRepository.remove("p999") is True


def test_index_repo_get_all_returns_copy():
    _setup()
    IndexRepository.set("p1", {"events_count": 5})
    a = IndexRepository.get_all()
    a.pop("p1")
    b = IndexRepository.get_all()
    assert "p1" in b


def test_index_repo_caching():
    """After set(), the cache should be populated so load_index() isn't called again."""
    _setup()
    IndexRepository.set("p1", {"events_count": 1})
    # Mutate the backing store directly - the repo should return cached data
    _fake_index["p1"]["events_count"] = 999
    assert IndexRepository.get("p1")["events_count"] == 1


def test_index_repo_invalidate_forces_reload():
    _setup()
    IndexRepository.set("p1", {"events_count": 1})
    _fake_index["p1"]["events_count"] = 42
    IndexRepository.invalidate()
    assert IndexRepository.get("p1")["events_count"] == 42


# ===================================================================
# validators.check_plant / check_event / check_garden
# ===================================================================

def test_check_plant_valid():
    errors = validators.check_plant({"id": "p1", "strain": "Haze"})
    assert errors == []


def test_check_plant_missing_id():
    errors = validators.check_plant({"strain": "Haze"})
    assert len(errors) >= 1
    assert any("id" in e.lower() for e in errors)


def test_check_plant_missing_strain():
    errors = validators.check_plant({"id": "p1"})
    assert len(errors) >= 1
    assert any("strain" in e.lower() for e in errors)


def test_check_plant_not_a_dict():
    errors = validators.check_plant("bad")
    assert errors == ["Plant data must be a dict"]


def test_check_event_valid():
    errors = validators.check_event({"id": "e1", "ts": "2025-01-01", "type": "watering"})
    assert errors == []


def test_check_event_missing_fields():
    errors = validators.check_event({})
    assert len(errors) >= 3  # id, ts, type


def test_check_event_not_a_dict():
    errors = validators.check_event(42)
    assert errors == ["Event data must be a dict"]


def test_check_garden_valid():
    errors = validators.check_garden({"id": "g1", "name": "My Garden"})
    assert errors == []


def test_check_garden_missing_name():
    errors = validators.check_garden({"id": "g1"})
    assert len(errors) >= 1
    assert any("name" in e.lower() for e in errors)


def test_check_garden_not_a_dict():
    errors = validators.check_garden([])
    assert errors == ["Garden data must be a dict"]


# ---------------------------------------------------------------------------
# GardenRepository - list_all, save, delete
# ---------------------------------------------------------------------------

def test_garden_repo_list_all_empty():
    _setup()
    gardens = GardenRepository.list_all()
    assert gardens == []


def test_garden_repo_list_all():
    _setup()
    _fake_gardens["g1"] = {"id": "g1", "name": "Garden A"}
    _fake_gardens["g2"] = {"id": "g2", "name": "Garden B"}
    GardenRepository.invalidate()
    gardens = GardenRepository.list_all()
    assert len(gardens) == 2


def test_garden_repo_save():
    _setup()
    garden = {"id": "g1", "name": "New Garden"}
    ok = GardenRepository.save(garden)
    assert ok is True
    assert _fake_gardens.get("g1") is not None
    assert _fake_gardens["g1"]["name"] == "New Garden"


def test_garden_repo_save_invalidates_cache():
    _setup()
    _fake_gardens["g1"] = {"id": "g1", "name": "Old"}
    GardenRepository.list_all()  # populate cache
    GardenRepository.save({"id": "g2", "name": "New"})
    gardens = GardenRepository.list_all()
    assert len(gardens) == 2


def test_garden_repo_delete():
    _setup()
    _fake_gardens["g1"] = {"id": "g1", "name": "To Delete"}
    ok = GardenRepository.delete("g1")
    assert ok is True
    assert "g1" not in _fake_gardens


def test_garden_repo_delete_invalidates_cache():
    _setup()
    _fake_gardens["g1"] = {"id": "g1", "name": "Will Delete"}
    GardenRepository.list_all()  # populate cache
    GardenRepository.delete("g1")
    gardens = GardenRepository.list_all()
    assert len(gardens) == 0


# ---------------------------------------------------------------------------
# EventRepository.update_event
# ---------------------------------------------------------------------------

def test_event_repo_update_event():
    _setup()
    _fake_events["p1"] = {
        "plant_id": "p1",
        "penalty": 0,
        "events": [
            {"id": "e1", "ts": "2025-01-01", "type": "watering", "notes": "old"},
            {"id": "e2", "ts": "2025-01-02", "type": "feeding"},
        ],
    }
    EventRepository.invalidate()
    updated = {"id": "e1", "ts": "2025-01-01", "type": "watering", "notes": "updated"}
    ok = EventRepository.update_event("p1", "e1", updated)
    assert ok is True
    data = EventRepository.get("p1")
    matched = [e for e in data["events"] if e["id"] == "e1"]
    assert len(matched) == 1
    assert matched[0]["notes"] == "updated"


def test_event_repo_update_event_missing_plant():
    _setup()
    ok = EventRepository.update_event("nonexistent", "e1", {"type": "log"})
    assert ok is False


def test_event_repo_update_event_missing_event():
    _setup()
    _fake_events["p1"] = {
        "plant_id": "p1",
        "penalty": 0,
        "events": [{"id": "e1", "ts": "2025-01-01", "type": "watering"}],
    }
    EventRepository.invalidate()
    ok = EventRepository.update_event("p1", "nonexistent", {"type": "log"})
    assert ok is False


def test_event_repo_update_preserves_id():
    _setup()
    _fake_events["p1"] = {
        "plant_id": "p1",
        "penalty": 0,
        "events": [{"id": "e1", "ts": "2025-01-01", "type": "watering"}],
    }
    EventRepository.invalidate()
    # Try to update with a different id field - should be overwritten
    EventRepository.update_event("p1", "e1", {"id": "wrong", "type": "feeding"})
    data = EventRepository.get("p1")
    assert data["events"][0]["id"] == "e1"

