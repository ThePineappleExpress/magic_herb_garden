"""Tests for validators.py - schema validation (bool API and error-list API)."""

from validators import (
    validate_plant,
    validate_event,
    validate_garden,
    check_plant,
    check_event,
    check_garden,
)


# ---------------------------------------------------------------------------
# validate_plant (bool API)
# ---------------------------------------------------------------------------

def test_validate_plant_valid():
    plant = {"id": "p1", "strain": "Northern Lights"}
    assert validate_plant(plant) is True


def test_validate_plant_valid_with_extras():
    plant = {
        "id": "p1",
        "strain": "Northern Lights",
        "seedbank": "Sensi Seeds",
        "genes": "indica",
        "status": "active",
    }
    assert validate_plant(plant) is True


def test_validate_plant_missing_id():
    plant = {"strain": "Northern Lights"}
    assert validate_plant(plant) is False


def test_validate_plant_missing_strain():
    plant = {"id": "p1"}
    assert validate_plant(plant) is False


def test_validate_plant_empty_dict():
    assert validate_plant({}) is False


def test_validate_plant_wrong_type_id():
    plant = {"id": 123, "strain": "Northern Lights"}
    assert validate_plant(plant) is False


# ---------------------------------------------------------------------------
# validate_event (bool API)
# ---------------------------------------------------------------------------

def test_validate_event_valid():
    event = {"id": "e1", "ts": "2025-01-01T00:00:00", "type": "watering"}
    assert validate_event(event) is True


def test_validate_event_valid_with_extras():
    event = {
        "id": "e1",
        "ts": "2025-01-01T00:00:00",
        "type": "feeding",
        "notes": "Fed with bloom nutes",
    }
    assert validate_event(event) is True


def test_validate_event_missing_ts():
    event = {"id": "e1", "type": "watering"}
    assert validate_event(event) is False


def test_validate_event_missing_type():
    event = {"id": "e1", "ts": "2025-01-01T00:00:00"}
    assert validate_event(event) is False


def test_validate_event_empty_dict():
    assert validate_event({}) is False


# ---------------------------------------------------------------------------
# validate_garden (bool API)
# ---------------------------------------------------------------------------

def test_validate_garden_valid():
    garden = {"id": "g1", "name": "Tent #1"}
    assert validate_garden(garden) is True


def test_validate_garden_valid_with_extras():
    garden = {
        "id": "g1",
        "name": "Tent #1",
        "type": "indoor",
        "plants": [],
        "created_at": "2025-01-01T00:00:00",
    }
    assert validate_garden(garden) is True


def test_validate_garden_missing_name():
    garden = {"id": "g1"}
    assert validate_garden(garden) is False


def test_validate_garden_missing_id():
    garden = {"name": "Tent #1"}
    assert validate_garden(garden) is False


def test_validate_garden_empty_dict():
    assert validate_garden({}) is False


# ---------------------------------------------------------------------------
# check_plant (error-list API) - extended coverage
# ---------------------------------------------------------------------------

def test_check_plant_valid_returns_empty():
    assert check_plant({"id": "p1", "strain": "Haze"}) == []


def test_check_plant_missing_both_fields():
    errors = check_plant({})
    assert len(errors) >= 2, f"Expected >=2 errors, got {errors}"


def test_check_plant_non_dict():
    errors = check_plant("not a dict")
    assert errors == ["Plant data must be a dict"]


def test_check_plant_none():
    errors = check_plant(None)
    assert errors == ["Plant data must be a dict"]


def test_check_plant_list_input():
    errors = check_plant([{"id": "p1", "strain": "Haze"}])
    assert errors == ["Plant data must be a dict"]


# ---------------------------------------------------------------------------
# check_event (error-list API) - extended coverage
# ---------------------------------------------------------------------------

def test_check_event_valid_returns_empty():
    assert check_event({"id": "e1", "ts": "2025-01-01", "type": "log"}) == []


def test_check_event_missing_all_fields():
    errors = check_event({})
    assert len(errors) >= 3, f"Expected >=3 errors, got {errors}"


def test_check_event_non_dict():
    errors = check_event(42)
    assert errors == ["Event data must be a dict"]


# ---------------------------------------------------------------------------
# check_garden (error-list API) - extended coverage
# ---------------------------------------------------------------------------

def test_check_garden_valid_returns_empty():
    assert check_garden({"id": "g1", "name": "Tent"}) == []


def test_check_garden_missing_all_fields():
    errors = check_garden({})
    assert len(errors) >= 2, f"Expected >=2 errors, got {errors}"


def test_check_garden_non_dict():
    errors = check_garden("not a dict")
    assert errors == ["Garden data must be a dict"]
