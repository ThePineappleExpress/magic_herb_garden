"""Tests for service layer functions (Phase 1).

Covers:
  - garden_service: get_garden_plants_view, filter_plants, sort_plants
  - plant_service: create_plant, apply_event_side_effects
  - event_service: get_events_sorted, add_event
  - settings_service: get_settings, set_setting, has_password
  - formatting: get_health_indicator, get_nutrient_status, format_relative_time

Storage is monkey-patched on the data module object so no sys.modules
pollution occurs.
"""

import copy
from datetime import date

import data as _data_mod
from data import (
    GardenRepository, PlantRepository, EventRepository,
    IndexRepository, SettingsRepository,
)
from services.garden_service import get_garden_plants_view, filter_plants, sort_plants
from services.plant_service import create_plant, apply_event_side_effects
from services.event_service import get_events_sorted, add_event
from services.formatting import get_health_indicator, get_nutrient_status, format_relative_time

# Settings service uses SettingsRepository which is already patched through data module
from services.settings_service import get_settings, set_setting, has_password

# ---------------------------------------------------------------------------
# In-memory fake backing stores
# ---------------------------------------------------------------------------

_fake_gardens: dict = {}
_fake_events: dict = {}
_fake_index: dict = {}
_fake_settings: dict = {}

_real_storage = _data_mod.storage


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
        return copy.deepcopy(_fake_settings)

    @staticmethod
    def save_settings(settings):
        global _fake_settings
        _fake_settings = copy.deepcopy(settings)
        return True


# Patch data module's storage reference
_data_mod.storage = _FakeStorage
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


def _seed_garden(gid="g1", plants=None):
    _fake_gardens[gid] = {"id": gid, "name": "Test", "plants": plants or []}


def _make_plant(pid="p1", strain="NL", **kwargs):
    p = {"id": pid, "strain": strain, "status": "veg"}
    p.update(kwargs)
    return p


# ===================================================================
# garden_service
# ===================================================================

def test_get_garden_plants_view_empty():
    _setup()
    _seed_garden("g1", [])
    result = get_garden_plants_view("g1")
    assert result == []


def test_get_garden_plants_view_basic():
    _setup()
    _seed_garden("g1", [_make_plant("p1", "Northern Lights", date_planted="2025-06-01", days_to_flower=60)])
    result = get_garden_plants_view("g1", today=date(2025, 7, 1))
    assert len(result) == 1
    assert result[0]["strain"] == "Northern Lights"
    assert result[0]["id"] == "p1"


def test_get_garden_plants_view_none_garden():
    _setup()
    assert get_garden_plants_view(None) == []


def test_filter_plants_by_search():
    items = [
        {"strain": "Northern Lights", "seedbank": "Sensi", "notes": "", "medium": "soil", "genes": "Indica"},
        {"strain": "Blue Dream", "seedbank": "HSO", "notes": "", "medium": "coco", "genes": "Hybrid"},
    ]
    result = filter_plants(items, search_text="blue")
    assert len(result) == 1
    assert result[0]["strain"] == "Blue Dream"


def test_filter_plants_active_only():
    items = [
        {"strain": "A", "harvest_status": "harvested"},
        {"strain": "B", "harvest_status": "42"},
    ]
    result = filter_plants(items, active_only=True)
    assert len(result) == 1
    assert result[0]["strain"] == "B"


def test_sort_plants_by_strain():
    items = [
        {"strain": "Zkittlez"},
        {"strain": "AK-47"},
        {"strain": "Blue Dream"},
    ]
    result = sort_plants(items, key="strain", ascending=True)
    assert [r["strain"] for r in result] == ["AK-47", "Blue Dream", "Zkittlez"]


def test_sort_plants_descending():
    items = [{"strain": "A"}, {"strain": "B"}]
    result = sort_plants(items, ascending=False)
    assert result[0]["strain"] == "B"


# ===================================================================
# plant_service
# ===================================================================

def test_create_plant():
    _setup()
    _seed_garden("g1")
    plant = _make_plant("p1", "Haze")
    assert create_plant("g1", plant) is True
    got = PlantRepository.get("g1", "p1")
    assert got is not None
    assert got["strain"] == "Haze"


def test_create_plant_no_garden():
    _setup()
    assert create_plant(None, _make_plant()) is False


def test_apply_side_effects_top():
    _setup()
    _seed_garden("g1", [_make_plant("p1", penalty=0)])
    apply_event_side_effects("g1", "p1", "top")
    got = PlantRepository.get("g1", "p1")
    assert got["penalty"] == 7


def test_apply_side_effects_prune_accumulates():
    _setup()
    _seed_garden("g1", [_make_plant("p1", penalty=7)])
    apply_event_side_effects("g1", "p1", "prune")
    got = PlantRepository.get("g1", "p1")
    assert got["penalty"] == 14


def test_apply_side_effects_flip():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    apply_event_side_effects("g1", "p1", "flip")
    got = PlantRepository.get("g1", "p1")
    assert got["stage"] == "flowering"
    assert "flip_date" in got


def test_apply_side_effects_harvest():
    _setup()
    _seed_garden("g1", [_make_plant("p1")])
    apply_event_side_effects("g1", "p1", "harvest")
    got = PlantRepository.get("g1", "p1")
    assert got["stage"] == "harvested"
    assert "harvest_date" in got


def test_apply_side_effects_missing_plant():
    _setup()
    _seed_garden("g1", [])
    assert apply_event_side_effects("g1", "p999", "top") is False


# ===================================================================
# event_service
# ===================================================================

def test_get_events_sorted_empty():
    _setup()
    assert get_events_sorted("p999") == []


def test_get_events_sorted_ordering():
    _setup()
    _fake_events["p1"] = {
        "plant_id": "p1",
        "penalty": 0,
        "events": [
            {"id": "e1", "ts": "2025-01-01", "type": "watering"},
            {"id": "e2", "ts": "2025-01-03", "type": "feeding"},
            {"id": "e3", "ts": "2025-01-02", "type": "log"},
        ],
    }
    EventRepository.invalidate()
    result = get_events_sorted("p1", reverse=True)
    assert [e["id"] for e in result] == ["e2", "e3", "e1"]


def test_get_events_sorted_ascending():
    _setup()
    _fake_events["p1"] = {
        "plant_id": "p1", "penalty": 0,
        "events": [
            {"id": "e1", "ts": "2025-01-03", "type": "a"},
            {"id": "e2", "ts": "2025-01-01", "type": "b"},
        ],
    }
    EventRepository.invalidate()
    result = get_events_sorted("p1", reverse=False)
    assert result[0]["id"] == "e2"


def test_add_event_via_service():
    _setup()
    _fake_events["p1"] = {"plant_id": "p1", "penalty": 0, "events": []}
    EventRepository.invalidate()
    ok = add_event("p1", {"id": "e1", "ts": "2025-01-01", "type": "watering"})
    assert ok is True
    events = get_events_sorted("p1")
    assert len(events) == 1


# ===================================================================
# settings_service
# ===================================================================

def test_get_and_set_setting():
    _setup()
    set_setting("theme", "purple")
    assert get_settings().get("theme") == "purple"


def test_has_password_false():
    _setup()
    assert has_password() is False


def test_has_password_true():
    _setup()
    global _fake_settings
    _fake_settings = {"password": {"hash": "abc", "salt": "def"}}
    SettingsRepository.invalidate()
    assert has_password() is True


# ===================================================================
# formatting
# ===================================================================

def test_get_health_indicator_healthy():
    plant = {"leaf_color": "normal", "leaf_morphology": "normal",
             "deficiencies": {}, "excess": {}}
    assert get_health_indicator(plant) == "Healthy"


def test_get_health_indicator_minor():
    plant = {"leaf_color": "normal", "leaf_morphology": "normal",
             "deficiencies": {"n": True}, "excess": {}}
    assert get_health_indicator(plant) == "Minor issues"


def test_get_health_indicator_severe():
    plant = {
        "leaf_color": "yellow", "leaf_morphology": "curled",
        "deficiencies": {"n": True, "p": True, "k": True, "ca": True},
        "excess": {},
    }
    assert get_health_indicator(plant) == "Severe issues"


def test_get_nutrient_status():
    plant = {"deficiencies": {"n": True}, "excess": {"p": True}}
    assert get_nutrient_status(plant, "n") == "deficient"
    assert get_nutrient_status(plant, "p") == "excess"
    assert get_nutrient_status(plant, "k") is None


def test_format_relative_time():
    assert format_relative_time(None) == "-"
    assert format_relative_time(0) == "today"
    assert format_relative_time(1) == "1 day ago"
    assert format_relative_time(14) == "14 days ago"


# ===========================================================================
# Phase 2 tests - Repository integration patterns used by Big Four screens
# ===========================================================================


# --------------- garden_view patterns (PlantRepository + IndexRepository) ------

def test_plant_list_for_garden():
    """garden_view.refresh_plants uses PlantRepository.list_for_garden."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [
            {"id": "p1", "strain": "Haze", "stage": "veg"},
            {"id": "p2", "strain": "Kush", "stage": "flowering"},
        ],
    }
    plants = PlantRepository.list_for_garden("g1")
    assert len(plants) == 2
    assert plants[0]["strain"] == "Haze"


def test_plant_remove():
    """garden_view.on_delete_selected uses PlantRepository.remove."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [
            {"id": "p1", "strain": "Haze"},
            {"id": "p2", "strain": "Kush"},
        ],
    }
    ok = PlantRepository.remove("g1", "p1")
    assert ok is True
    remaining = PlantRepository.list_for_garden("g1")
    assert len(remaining) == 1
    assert remaining[0]["id"] == "p2"


def test_index_get_all():
    """garden_view.refresh_plants uses IndexRepository.get_all for last_event_ts."""
    _setup()
    global _fake_index
    _fake_index = {
        "p1": {"last_event_ts": "2025-06-01", "event_count": 5},
        "p2": {"last_event_ts": "2025-07-15", "event_count": 3},
    }
    IndexRepository.invalidate()
    index = IndexRepository.get_all()
    assert index["p1"]["last_event_ts"] == "2025-06-01"
    assert index["p2"]["event_count"] == 3


# --------------- plant_details patterns (EventRepository) ------------------

def test_event_repo_get_returns_events():
    """plant_details._load_and_display_events uses EventRepository.get."""
    _setup()
    _fake_events["p1"] = {
        "plant_id": "p1",
        "events": [
            {"id": "e1", "type": "watering", "ts": "2025-06-01"},
            {"id": "e2", "type": "feeding", "ts": "2025-06-02"},
        ],
    }
    data = EventRepository.get("p1")
    assert data is not None
    events = data.get("events", [])
    assert len(events) == 2
    assert events[0]["type"] == "watering"


def test_event_repo_get_returns_none_for_missing():
    """plant_details handles None from EventRepository.get gracefully."""
    _setup()
    data = EventRepository.get("nonexistent")
    assert data is None


def test_event_repo_save_and_get_roundtrip():
    """plant_details photo handler uses EventRepository.save then get."""
    _setup()
    EventRepository.save("p1", {
        "plant_id": "p1",
        "events": [{"id": "e1", "type": "log", "ts": "2025-06-01"}],
    })
    data = EventRepository.get("p1")
    assert data is not None
    assert len(data["events"]) == 1
    assert data["events"][0]["id"] == "e1"


# --------------- add_event patterns (GardenRepository + side-effects) ------

def test_garden_repo_get():
    """add_event._detect_light_schedule uses GardenRepository.get."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "type": "indoor",
        "light_schedule": [18, 6],
        "plants": [],
    }
    garden = GardenRepository.get("g1")
    assert garden is not None
    assert garden["type"] == "indoor"
    assert garden["light_schedule"] == [18, 6]


def test_garden_repo_get_returns_none():
    """GardenRepository.get returns None for missing garden."""
    _setup()
    assert GardenRepository.get("nonexistent") is None


def test_apply_side_effects_via_service():
    """add_event now calls apply_event_side_effects from plant_service."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [{"id": "p1", "stage": "veg", "penalty": 0}],
    }
    PlantRepository.invalidate()
    ok = apply_event_side_effects("g1", "p1", "top")
    assert ok is True
    plant = PlantRepository.get("g1", "p1")
    assert plant["penalty"] == 7


def test_apply_side_effects_flip():
    """Flip event sets stage to flowering + flip_date."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [{"id": "p1", "stage": "veg"}],
    }
    PlantRepository.invalidate()
    ok = apply_event_side_effects("g1", "p1", "flip")
    assert ok is True
    plant = PlantRepository.get("g1", "p1")
    assert plant["stage"] == "flowering"
    assert "flip_date" in plant


def test_apply_side_effects_harvest():
    """Harvest event sets stage to harvested + harvest_date."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [{"id": "p1", "stage": "flowering"}],
    }
    PlantRepository.invalidate()
    ok = apply_event_side_effects("g1", "p1", "harvest")
    assert ok is True
    plant = PlantRepository.get("g1", "p1")
    assert plant["stage"] == "harvested"
    assert "harvest_date" in plant


def test_apply_side_effects_stacks_penalty():
    """Multiple top/prune events stack 7-day penalty."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [{"id": "p1", "stage": "veg", "penalty": 0}],
    }
    PlantRepository.invalidate()
    apply_event_side_effects("g1", "p1", "top")
    apply_event_side_effects("g1", "p1", "prune")
    plant = PlantRepository.get("g1", "p1")
    assert plant["penalty"] == 14


# --------------- timeline_view patterns (EventRepository + PlantRepository) --

def test_event_repo_get_with_plant_lookup():
    """timeline_view.set_plant + load_plant both use EventRepository.get."""
    _setup()
    _fake_gardens["g1"] = {
        "id": "g1",
        "plants": [{"id": "p1", "strain": "Purple Haze"}],
    }
    _fake_events["p1"] = {
        "plant_id": "p1",
        "events": [
            {"id": "e1", "type": "watering", "ts": "2025-06-01"},
            {"id": "e2", "type": "feeding", "ts": "2025-06-05"},
        ],
    }
    # Simulate what timeline_view.set_plant does: lookup plant then load events
    plants = PlantRepository.list_for_garden("g1")
    target = None
    for p in plants:
        if str(p.get("id")) == "p1":
            target = p
            break
    assert target is not None
    assert target["strain"] == "Purple Haze"

    data = EventRepository.get("p1")
    events = data.get("events", []) if data else []
    assert len(events) == 2


def test_plant_list_for_garden_empty():
    """timeline_view handles empty garden gracefully."""
    _setup()
    _fake_gardens["g1"] = {"id": "g1", "plants": []}
    plants = PlantRepository.list_for_garden("g1")
    assert plants == []


def test_plant_list_for_garden_missing():
    """timeline_view handles missing garden (returns [])."""
    _setup()
    plants = PlantRepository.list_for_garden("nonexistent")
    assert plants == []


# ---------------------------------------------------------------------------
# settings_service - extended coverage
# ---------------------------------------------------------------------------

def test_get_setting_default():
    _setup()
    from services.settings_service import get_setting
    result = get_setting("nonexistent_key", "fallback")
    assert result == "fallback"


def test_get_setting_existing():
    _setup()
    from services.settings_service import set_setting, get_setting
    set_setting("language", "english")
    assert get_setting("language") == "english"


def test_get_theme_name_default():
    _setup()
    from services.settings_service import get_theme_name
    result = get_theme_name()
    assert isinstance(result, str)
    assert len(result) > 0, "Should return a default theme name"


def test_get_theme_name_custom():
    _setup()
    from services.settings_service import set_setting, get_theme_name
    set_setting("theme", "green")
    result = get_theme_name()
    assert result == "green"


# ---------------------------------------------------------------------------
# formatting - edge cases
# ---------------------------------------------------------------------------

def test_health_indicator_moderate():
    """Test the moderate issues branch."""
    plant = {"leaf_color": "yellow", "leaf_morphology": "normal"}
    result = get_health_indicator(plant)
    assert isinstance(result, str)
    assert len(result) > 0


def test_format_relative_time_just_now():
    from datetime import datetime
    now = datetime.now().isoformat()
    result = format_relative_time(now)
    assert isinstance(result, str)
    assert len(result) > 0


def test_format_relative_time_none():
    result = format_relative_time(None)
    assert isinstance(result, str)


def test_format_relative_time_empty():
    result = format_relative_time("")
    assert isinstance(result, str)


# ---------------------------------------------------------------------------
# garden_service - edge cases
# ---------------------------------------------------------------------------

def test_filter_plants_empty_search():
    _setup()
    plants = [
        {"id": "p1", "strain": "Northern Lights", "status": "active"},
        {"id": "p2", "strain": "Haze", "status": "harvested"},
    ]
    result = filter_plants(plants, search_text="")
    assert len(result) == 2, "Empty search should return all"


def test_sort_plants_no_plants():
    _setup()
    result = sort_plants([], key="strain")
    assert result == []


def test_sort_plants_by_strain_ascending():
    _setup()
    plants = [
        {"strain": "Zkittlez"},
        {"strain": "Amnesia"},
        {"strain": "Blueberry"},
    ]
    result = sort_plants(plants, key="strain", ascending=True)
    assert result[0]["strain"] == "Amnesia"
    assert result[-1]["strain"] == "Zkittlez"
