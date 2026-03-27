"""Integration tests - end-to-end flows through multiple layers.

Uses the same _FakeStorage pattern to test cross-module interactions.
"""

import copy
import json
import os
import shutil
import tempfile
from pathlib import Path

import data as _data_mod
from data import (
    GardenRepository,
    PlantRepository,
    EventRepository,
    IndexRepository,
    SettingsRepository,
)
from services.plant_service import create_plant, apply_event_side_effects
from services.event_service import get_events_sorted, add_event
from services.garden_service import get_garden_plants_view


# ---------------------------------------------------------------------------
# In-memory fake storage
# ---------------------------------------------------------------------------

_fake_gardens: dict = {}
_fake_events: dict = {}
_fake_index: dict = {}
_fake_settings: dict = {}


class _FakeStorage:
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
        return copy.deepcopy(_fake_settings)

    @staticmethod
    def save_settings(s):
        global _fake_settings
        _fake_settings = copy.deepcopy(s)
        return True


_data_mod.storage = _FakeStorage


def _setup():
    global _fake_gardens, _fake_events, _fake_index, _fake_settings
    _fake_gardens = {}
    _fake_events = {}
    _fake_index = {}
    _fake_settings = {}
    GardenRepository.invalidate()
    PlantRepository.invalidate()
    EventRepository.invalidate()
    IndexRepository.invalidate()
    SettingsRepository.invalidate()


# ---------------------------------------------------------------------------
# Full plant lifecycle
# ---------------------------------------------------------------------------

def test_full_plant_lifecycle():
    """Create garden → add plant → add events → verify timeline data."""
    _setup()

    # Create a garden
    garden = {"id": "g1", "name": "Test Tent", "type": "indoor", "plants": []}
    GardenRepository.save(garden)

    # Create a plant via service
    plant_data = {
        "id": "p1",
        "strain": "Northern Lights",
        "seedbank": "Sensi Seeds",
        "date_planted": "2025-01-01",
        "status": "active",
    }
    ok = create_plant("g1", plant_data)
    assert ok is True, "create_plant should succeed"

    # Add events
    events_to_add = [
        {"id": "e1", "ts": "2025-01-05T10:00:00", "type": "watering", "volume_l": 0.5},
        {"id": "e2", "ts": "2025-01-10T10:00:00", "type": "feeding", "volume_l": 1.0},
        {"id": "e3", "ts": "2025-01-15T10:00:00", "type": "top"},
        {"id": "e4", "ts": "2025-01-20T10:00:00", "type": "prune"},
        {"id": "e5", "ts": "2025-02-01T10:00:00", "type": "flip"},
    ]
    for event in events_to_add:
        ok = add_event("p1", event)
        assert ok is True, f"add_event should succeed for {event['id']}"

    # Verify events are stored and sorted
    sorted_events = get_events_sorted("p1", reverse=False)
    assert len(sorted_events) >= 5, f"Expected >=5 events, got {len(sorted_events)}"

    # Verify chronological order
    timestamps = [e.get("ts", "") for e in sorted_events]
    assert timestamps == sorted(timestamps), "Events should be sorted by timestamp"


def test_event_side_effects_accumulate():
    """Top → Prune → verify counts accumulate on the plant."""
    _setup()

    garden = {"id": "g1", "name": "Test", "plants": [
        {"id": "p1", "strain": "Haze", "topped": 0, "pruned": 0, "status": "active"},
    ]}
    GardenRepository.save(garden)

    # Apply top events
    plant = PlantRepository.get("g1", "p1")
    assert plant is not None

    apply_event_side_effects("g1", "p1", "top")
    plant = PlantRepository.get("g1", "p1")
    assert plant.get("penalty", 0) == 7, "First top should add 7 penalty days"

    apply_event_side_effects("g1", "p1", "top")
    plant = PlantRepository.get("g1", "p1")
    assert plant.get("penalty", 0) == 14, "Second top should add another 7 penalty days"

    # Apply prune
    apply_event_side_effects("g1", "p1", "prune")
    plant = PlantRepository.get("g1", "p1")
    assert plant.get("penalty", 0) == 21, "Prune should add 7 more penalty days"


def test_event_side_effects_flip():
    """Flip event should set flipped flag."""
    _setup()

    garden = {"id": "g1", "name": "Test", "plants": [
        {"id": "p1", "strain": "Kush", "status": "active"},
    ]}
    GardenRepository.save(garden)

    apply_event_side_effects("g1", "p1", "flip")
    plant = PlantRepository.get("g1", "p1")
    assert plant.get("stage") == "flowering", "Flip should set stage to flowering"
    assert plant.get("flip_date") is not None, "Flip should set flip_date"


def test_multiple_gardens_isolation():
    """Plants in different gardens should not interfere."""
    _setup()

    g1 = {"id": "g1", "name": "Garden A", "plants": [
        {"id": "p1", "strain": "Strain A"},
    ]}
    g2 = {"id": "g2", "name": "Garden B", "plants": [
        {"id": "p2", "strain": "Strain B"},
    ]}
    GardenRepository.save(g1)
    GardenRepository.save(g2)

    p1 = PlantRepository.get("g1", "p1")
    p2 = PlantRepository.get("g2", "p2")
    assert p1 is not None and p1["strain"] == "Strain A"
    assert p2 is not None and p2["strain"] == "Strain B"

    # p1 should not be found in g2
    assert PlantRepository.get("g2", "p1") is None
    assert PlantRepository.get("g1", "p2") is None


def test_garden_view_with_events():
    """get_garden_plants_view returns plant data with event info."""
    _setup()

    garden = {"id": "g1", "name": "Test", "plants": [
        {"id": "p1", "strain": "Haze", "date_planted": "2025-01-01", "status": "active"},
    ]}
    GardenRepository.save(garden)

    _fake_events["p1"] = {
        "plant_id": "p1",
        "penalty": 0,
        "events": [
            {"id": "e1", "ts": "2025-01-01T10:00:00", "type": "watering"},
            {"id": "e2", "ts": "2025-01-05T10:00:00", "type": "feeding"},
        ],
    }
    EventRepository.invalidate()

    result = get_garden_plants_view("g1")
    assert len(result) == 1
    assert result[0]["strain"] == "Haze"


def test_settings_persist():
    """Settings round-trip through repository."""
    _setup()

    SettingsRepository.set("language", "english")
    SettingsRepository.set("theme", "green")

    settings = SettingsRepository.get_all()
    assert settings.get("language") == "english"
    assert settings.get("theme") == "green"


# ---------------------------------------------------------------------------
# .weed export/import roundtrip (real file I/O)
# ---------------------------------------------------------------------------

def test_weed_export_import_roundtrip():
    """Create data → .weed export → import → verify identical."""
    from weed_format import write_weed, read_weed

    tmp = tempfile.mkdtemp(prefix="mht_integ_weed_")
    try:
        gardens_data = [{
            "garden": {
                "id": "g1",
                "name": "Integration Test Garden",
                "plants": [
                    {"id": "p1", "strain": "Northern Lights"},
                    {"id": "p2", "strain": "Purple Haze"},
                ],
            },
            "events": {
                "p1": {"plant_id": "p1", "events": [
                    {"id": "e1", "ts": "2025-01-01", "type": "watering"},
                ]},
                "p2": {"plant_id": "p2", "events": [
                    {"id": "e2", "ts": "2025-01-02", "type": "feeding"},
                ]},
            },
        }]

        path = Path(tmp) / "roundtrip.weed"
        write_weed(path, gardens_data, include_photos=False)
        result = read_weed(path)

        assert len(result["gardens"]) == 1
        assert result["gardens"][0]["name"] == "Integration Test Garden"
        assert len(result["gardens"][0]["plants"]) == 2
        assert len(result["events"]) == 2
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Encrypt / decrypt cycle (real crypto)
# ---------------------------------------------------------------------------

def test_encrypt_decrypt_cycle():
    """Set password → encrypt → decrypt → data intact."""
    from crypto import encrypt_bytes, decrypt_bytes, is_encrypted
    from helpers import hash_password, verify_password, derive_encryption_key

    password = "test_password_123"
    stored = hash_password(password)

    assert verify_password(password, stored) is True
    assert verify_password("wrong", stored) is False

    key = derive_encryption_key(password, stored)
    assert len(key) == 32

    # Encrypt some data
    plaintext = b'{"id": "g1", "name": "Encrypted Garden"}'
    encrypted = encrypt_bytes(plaintext, key, aad=b"test")
    assert is_encrypted(encrypted) is True
    assert encrypted != plaintext

    # Decrypt
    decrypted = decrypt_bytes(encrypted, key, aad=b"test")
    assert decrypted == plaintext
