"""Tests for csv_export_screen.py - pure row-builder functions.

The module imports Kivy at the top level, so we use importlib + source
inspection to extract just the pure functions we need.
"""

import importlib
import sys
import types

# ---------------------------------------------------------------------------
# Import helpers: load only the pure functions without triggering Kivy
# ---------------------------------------------------------------------------

def _load_row_builders():
    """Extract _garden_base_row, _plant_base_row, _event_row from source."""
    import ast
    from pathlib import Path

    src = Path(__file__).resolve().parent.parent / "csv_export_screen.py"
    source = src.read_text()
    tree = ast.parse(source)

    # Collect function source for our target functions
    target_names = {"_garden_base_row", "_plant_base_row", "_event_row"}
    funcs = {}
    lines = source.splitlines(keepends=True)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in target_names:
            start = node.lineno - 1
            end = node.end_lineno
            func_source = "".join(lines[start:end])
            funcs[node.name] = func_source

    # Compile and exec in a clean namespace
    ns = {}
    for name, fsrc in funcs.items():
        exec(compile(fsrc, f"<{name}>", "exec"), ns)

    return ns["_garden_base_row"], ns["_plant_base_row"], ns["_event_row"]


_garden_base_row, _plant_base_row, _event_row = _load_row_builders()


# ---------------------------------------------------------------------------
# _garden_base_row
# ---------------------------------------------------------------------------

def test_garden_base_row_full():
    garden = {
        "id": "g1",
        "name": "Tent #1",
        "type": "indoor",
        "light_type": "LED",
        "light_wattage": "600",
        "light_schedule": ["18:00", "06:00"],
        "location": "Bedroom",
    }
    row = _garden_base_row(garden)
    assert row["garden_id"] == "g1"
    assert row["garden_name"] == "Tent #1"
    assert row["garden_type"] == "indoor"
    assert row["garden_light_type"] == "LED"
    assert row["garden_light_wattage"] == "600"
    assert row["garden_light_schedule_on"] == "18:00"
    assert row["garden_light_schedule_off"] == "06:00"
    assert row["garden_location"] == "Bedroom"


def test_garden_base_row_empty():
    row = _garden_base_row({})
    assert row["garden_id"] == ""
    assert row["garden_name"] == ""
    assert row["garden_type"] == ""
    assert row["garden_light_schedule_on"] == ""
    assert row["garden_light_schedule_off"] == ""


def test_garden_base_row_partial_schedule():
    garden = {"light_schedule": ["18:00"]}
    row = _garden_base_row(garden)
    assert row["garden_light_schedule_on"] == "18:00"
    assert row["garden_light_schedule_off"] == ""


def test_garden_base_row_no_schedule():
    garden = {"id": "g1", "name": "Test", "light_schedule": []}
    row = _garden_base_row(garden)
    assert row["garden_light_schedule_on"] == ""
    assert row["garden_light_schedule_off"] == ""


# ---------------------------------------------------------------------------
# _plant_base_row
# ---------------------------------------------------------------------------

def test_plant_base_row_full():
    plant = {
        "id": "p1",
        "strain": "Northern Lights",
        "seedbank": "Sensi Seeds",
        "date_planted": "2025-01-01",
        "location": "A1",
        "status": "active",
    }
    row = _plant_base_row(plant)
    assert row["plant_id"] == "p1"
    assert row["plant_strain"] == "Northern Lights"
    assert row["plant_seedbank"] == "Sensi Seeds"
    assert row["plant_date_planted"] == "2025-01-01"
    assert row["plant_location"] == "A1"
    assert row["plant_status"] == "active"


def test_plant_base_row_empty():
    row = _plant_base_row({})
    assert row["plant_id"] == ""
    assert row["plant_strain"] == ""
    assert row["plant_status"] == ""


def test_plant_base_row_missing_optional():
    plant = {"id": "p1", "strain": "Haze"}
    row = _plant_base_row(plant)
    assert row["plant_id"] == "p1"
    assert row["plant_seedbank"] == ""
    assert row["plant_location"] == ""


# ---------------------------------------------------------------------------
# _event_row
# ---------------------------------------------------------------------------

def test_event_row_full():
    event = {
        "id": "e1",
        "ts": "2025-01-01T10:00:00",
        "type": "feeding",
        "notes": "Fed with bloom nutes",
        "volume_l": 2.5,
        "water_temp_c": 22,
        "ph": 6.2,
        "ppm": 800,
        "feeding": {
            "grow_mix": 1.0,
            "bloom_mix": 2.0,
            "CalMag": 0.5,
        },
        "plant": {
            "plant_height": 45,
            "num_nodes": 8,
            "stage": "flower",
        },
        "environment": {
            "air_temp_c": 25,
            "rh_percent": 55,
            "vpd_kpa": 1.2,
        },
    }
    row = _event_row(event)
    assert row["event_id"] == "e1"
    assert row["event_type"] == "feeding"
    assert row["volume_l"] == 2.5
    assert row["ph"] == 6.2
    assert row["feeding_bloom_mix"] == 2.0
    assert row["feeding_calmag"] == 0.5
    assert row["plant_height"] == 45
    assert row["plant_stage"] == "flower"
    assert row["air_temp_c"] == 25
    assert row["rh_percent"] == 55


def test_event_row_empty():
    row = _event_row({})
    assert row["event_id"] == ""
    assert row["event_type"] == ""
    assert row["volume_l"] == ""
    assert row["feeding_grow_mix"] == ""
    assert row["plant_height"] == ""
    assert row["air_temp_c"] == ""


def test_event_row_watering_no_feeding():
    event = {
        "id": "e2",
        "ts": "2025-01-02T08:00:00",
        "type": "watering",
        "volume_l": 1.0,
        "ph": 6.5,
    }
    row = _event_row(event)
    assert row["event_type"] == "watering"
    assert row["volume_l"] == 1.0
    assert row["feeding_grow_mix"] == ""
    assert row["feeding_bloom_mix"] == ""


def test_event_row_log_only():
    event = {
        "id": "e3",
        "ts": "2025-01-03T12:00:00",
        "type": "log",
        "notes": "Looking great!",
    }
    row = _event_row(event)
    assert row["event_type"] == "log"
    assert row["event_notes"] == "Looking great!"
    assert row["volume_l"] == ""
