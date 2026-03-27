"""Tests for constants.py - event type normalization and canonical types."""

from constants import (
    normalize_event_type,
    ALL_EVENT_TYPES,
    EVENT_WATERING,
    EVENT_FEEDING,
    EVENT_LOG,
    EVENT_PLANTING,
    EVENT_TOP,
    EVENT_PRUNE,
    EVENT_FLIP,
    EVENT_HARVEST,
)


def test_all_event_types_contains_all_canonical():
    expected = {
        EVENT_WATERING, EVENT_FEEDING, EVENT_LOG, EVENT_PLANTING,
        EVENT_TOP, EVENT_PRUNE, EVENT_FLIP, EVENT_HARVEST,
    }
    assert set(ALL_EVENT_TYPES) == expected, f"ALL_EVENT_TYPES mismatch: {ALL_EVENT_TYPES}"


def test_all_event_types_has_8_entries():
    assert len(ALL_EVENT_TYPES) == 8, f"Expected 8 types, got {len(ALL_EVENT_TYPES)}"


def test_normalize_canonical_watering():
    assert normalize_event_type("watering") == EVENT_WATERING


def test_normalize_canonical_feeding():
    assert normalize_event_type("feeding") == EVENT_FEEDING


def test_normalize_canonical_log():
    assert normalize_event_type("log") == EVENT_LOG


def test_normalize_canonical_planted():
    assert normalize_event_type("planted") == EVENT_PLANTING


def test_normalize_canonical_top():
    assert normalize_event_type("top") == EVENT_TOP


def test_normalize_canonical_prune():
    assert normalize_event_type("prune") == EVENT_PRUNE


def test_normalize_canonical_flip():
    assert normalize_event_type("flip") == EVENT_FLIP


def test_normalize_canonical_harvest():
    assert normalize_event_type("harvest") == EVENT_HARVEST


def test_normalize_alias_water():
    assert normalize_event_type("water") == EVENT_WATERING


def test_normalize_alias_watered():
    assert normalize_event_type("watered") == EVENT_WATERING


def test_normalize_alias_feed():
    assert normalize_event_type("feed") == EVENT_FEEDING


def test_normalize_alias_fed():
    assert normalize_event_type("fed") == EVENT_FEEDING


def test_normalize_alias_note():
    assert normalize_event_type("note") == EVENT_LOG


def test_normalize_alias_notes():
    assert normalize_event_type("notes") == EVENT_LOG


def test_normalize_alias_plant():
    assert normalize_event_type("plant") == EVENT_PLANTING


def test_normalize_alias_planting():
    assert normalize_event_type("planting") == EVENT_PLANTING


def test_normalize_alias_topped():
    assert normalize_event_type("topped") == EVENT_TOP


def test_normalize_alias_topping():
    assert normalize_event_type("topping") == EVENT_TOP


def test_normalize_alias_pruned():
    assert normalize_event_type("pruned") == EVENT_PRUNE


def test_normalize_alias_pruning():
    assert normalize_event_type("pruning") == EVENT_PRUNE


def test_normalize_alias_flipped():
    assert normalize_event_type("flipped") == EVENT_FLIP


def test_normalize_alias_flipping():
    assert normalize_event_type("flipping") == EVENT_FLIP


def test_normalize_alias_harvested():
    assert normalize_event_type("harvested") == EVENT_HARVEST


def test_normalize_case_insensitive_upper():
    assert normalize_event_type("WATERING") == EVENT_WATERING


def test_normalize_case_insensitive_mixed():
    assert normalize_event_type("Feeding") == EVENT_FEEDING


def test_normalize_case_insensitive_alias():
    assert normalize_event_type("TOPPED") == EVENT_TOP


def test_normalize_strips_whitespace():
    assert normalize_event_type("  watering  ") == EVENT_WATERING


def test_normalize_unknown_returns_lowered():
    result = normalize_event_type("unknown_type")
    assert result == "unknown_type", f"Expected 'unknown_type', got {result}"


def test_normalize_unknown_preserves_lowering():
    result = normalize_event_type("SOMETHING_ELSE")
    assert result == "something_else"
