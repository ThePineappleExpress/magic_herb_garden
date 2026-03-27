"""Tests for storage.py - file I/O functions with temp directories.

Uses tempfile.mkdtemp() to create isolated test directories.
Patches storage module paths to point at temp dirs.
"""

import copy
import json
import os
import shutil
import tempfile
from pathlib import Path

import storage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_original_garden_dir = storage.GARDEN_DIR
_original_events_dir = storage.EVENTS_DIR
_original_index_path = storage.INDEX_PATH
_original_settings_path = storage.SETTINGS_PATH
_original_photos_dir = storage.PHOTOS_DIR
_original_photo_index = storage.PHOTO_INDEX


def _make_tmp_storage():
    """Create a temp dir and patch storage module paths."""
    tmp = tempfile.mkdtemp(prefix="mht_test_")
    storage.GARDEN_DIR = Path(tmp) / "garden"
    storage.EVENTS_DIR = Path(tmp) / "plants"
    storage.INDEX_PATH = Path(tmp) / "plants_index.json"
    storage.SETTINGS_PATH = Path(tmp) / "settings.json"
    storage.PHOTOS_DIR = Path(tmp) / "photos"
    storage.PHOTO_INDEX = Path(tmp) / "photos_index.json"
    return tmp


def _cleanup(tmp):
    """Remove temp dir and restore original storage paths."""
    shutil.rmtree(tmp, ignore_errors=True)
    storage.GARDEN_DIR = _original_garden_dir
    storage.EVENTS_DIR = _original_events_dir
    storage.INDEX_PATH = _original_index_path
    storage.SETTINGS_PATH = _original_settings_path
    storage.PHOTOS_DIR = _original_photos_dir
    storage.PHOTO_INDEX = _original_photo_index


# ---------------------------------------------------------------------------
# _read_json / _atomic_write_json
# ---------------------------------------------------------------------------

def test_read_json_missing_file():
    tmp = _make_tmp_storage()
    try:
        result = storage._read_json(Path(tmp) / "nonexistent.json")
        assert result is None, f"Expected None for missing file, got {result}"
    finally:
        _cleanup(tmp)


def test_read_json_empty_file():
    tmp = _make_tmp_storage()
    try:
        p = Path(tmp) / "empty.json"
        p.write_bytes(b"")
        result = storage._read_json(p)
        assert result is None, f"Expected None for empty file, got {result}"
    finally:
        _cleanup(tmp)


def test_read_json_valid_file():
    tmp = _make_tmp_storage()
    try:
        p = Path(tmp) / "data.json"
        p.write_bytes(json.dumps({"key": "value"}).encode())
        result = storage._read_json(p)
        assert result == {"key": "value"}, f"Got {result}"
    finally:
        _cleanup(tmp)


def test_read_json_corrupt_json():
    tmp = _make_tmp_storage()
    try:
        p = Path(tmp) / "bad.json"
        p.write_bytes(b"not valid json{{{")
        result = storage._read_json(p)
        assert result is None, f"Expected None for corrupt JSON, got {result}"
    finally:
        _cleanup(tmp)


def test_atomic_write_json_creates_file():
    tmp = _make_tmp_storage()
    try:
        p = Path(tmp) / "new.json"
        storage._atomic_write_json(p, {"hello": "world"})
        assert p.exists(), "File should exist after atomic write"
        data = json.loads(p.read_bytes())
        assert data == {"hello": "world"}
    finally:
        _cleanup(tmp)


def test_atomic_write_json_overwrites():
    tmp = _make_tmp_storage()
    try:
        p = Path(tmp) / "overwrite.json"
        storage._atomic_write_json(p, {"version": 1})
        storage._atomic_write_json(p, {"version": 2})
        data = json.loads(p.read_bytes())
        assert data["version"] == 2, f"Expected version 2, got {data}"
    finally:
        _cleanup(tmp)


def test_atomic_write_no_tmp_leftover():
    tmp = _make_tmp_storage()
    try:
        p = Path(tmp) / "clean.json"
        storage._atomic_write_json(p, {"clean": True})
        tmp_file = p.with_suffix(p.suffix + ".tmp")
        assert not tmp_file.exists(), f".tmp file should not remain: {tmp_file}"
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# Garden CRUD
# ---------------------------------------------------------------------------

def test_load_gardens_empty_dir():
    tmp = _make_tmp_storage()
    try:
        result = storage.load_gardens()
        assert result == [], f"Expected empty list, got {result}"
    finally:
        _cleanup(tmp)


def test_save_and_load_garden_roundtrip():
    tmp = _make_tmp_storage()
    try:
        garden = {"id": "g1", "name": "Test Garden", "plants": []}
        assert storage.save_garden(garden) is True
        loaded = storage.load_garden("g1")
        assert loaded is not None
        assert loaded["id"] == "g1"
        assert loaded["name"] == "Test Garden"
    finally:
        _cleanup(tmp)


def test_save_garden_no_id_fails():
    tmp = _make_tmp_storage()
    try:
        assert storage.save_garden({"name": "No ID"}) is False
    finally:
        _cleanup(tmp)


def test_load_gardens_multiple():
    tmp = _make_tmp_storage()
    try:
        storage.save_garden({"id": "g1", "name": "Garden A"})
        storage.save_garden({"id": "g2", "name": "Garden B"})
        gardens = storage.load_gardens()
        assert len(gardens) == 2
        names = {g["name"] for g in gardens}
        assert "Garden A" in names
        assert "Garden B" in names
    finally:
        _cleanup(tmp)


def test_delete_garden_removes_file():
    tmp = _make_tmp_storage()
    try:
        storage.save_garden({"id": "g1", "name": "To Delete", "plants": []})
        assert storage.load_garden("g1") is not None
        storage.delete_garden("g1")
        assert storage.load_garden("g1") is None
    finally:
        _cleanup(tmp)


def test_delete_garden_missing_noop():
    tmp = _make_tmp_storage()
    try:
        result = storage.delete_garden("nonexistent")
        # Should not raise and return True (file simply doesn't exist)
        assert result is True
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# Plant helpers
# ---------------------------------------------------------------------------

def test_get_plants_empty_garden():
    tmp = _make_tmp_storage()
    try:
        storage.save_garden({"id": "g1", "name": "Empty", "plants": []})
        plants = storage.get_plants_for_garden("g1")
        assert plants == []
    finally:
        _cleanup(tmp)


def test_add_and_get_plant():
    tmp = _make_tmp_storage()
    try:
        storage.save_garden({"id": "g1", "name": "Test", "plants": []})
        plant = {"id": "p1", "strain": "Northern Lights"}
        storage.add_plant_to_garden("g1", plant)
        plants = storage.get_plants_for_garden("g1")
        assert len(plants) == 1
        assert plants[0]["strain"] == "Northern Lights"
    finally:
        _cleanup(tmp)


def test_remove_plant():
    tmp = _make_tmp_storage()
    try:
        storage.save_garden({"id": "g1", "name": "Test", "plants": []})
        storage.add_plant_to_garden("g1", {"id": "p1", "strain": "Haze"})
        storage.add_plant_to_garden("g1", {"id": "p2", "strain": "Kush"})
        storage.remove_plant_from_garden("g1", "p1")
        plants = storage.get_plants_for_garden("g1")
        assert len(plants) == 1
        assert plants[0]["id"] == "p2"
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

def test_save_load_events_roundtrip():
    tmp = _make_tmp_storage()
    try:
        events_data = {
            "plant_id": "p1",
            "penalty": 0,
            "events": [
                {"id": "e1", "ts": "2025-01-01", "type": "watering"},
                {"id": "e2", "ts": "2025-01-02", "type": "feeding"},
            ],
        }
        assert storage.save_plant_events("p1", events_data) is True
        loaded = storage.load_plant_events("p1")
        assert loaded is not None
        assert len(loaded["events"]) == 2
        assert loaded["events"][0]["id"] == "e1"
    finally:
        _cleanup(tmp)


def test_load_events_missing():
    tmp = _make_tmp_storage()
    try:
        result = storage.load_plant_events("nonexistent")
        assert result is None
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

def test_save_load_settings_roundtrip():
    tmp = _make_tmp_storage()
    try:
        settings = {"language": "english", "theme": "green"}
        assert storage.save_settings(settings) is True
        loaded = storage.load_settings()
        assert loaded["language"] == "english"
        assert loaded["theme"] == "green"
    finally:
        _cleanup(tmp)


def test_load_settings_missing():
    tmp = _make_tmp_storage()
    try:
        loaded = storage.load_settings()
        assert loaded == {}
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# Index
# ---------------------------------------------------------------------------

def test_save_load_index_roundtrip():
    tmp = _make_tmp_storage()
    try:
        index = {"p1": {"last_event_ts": "2025-01-01", "events_count": 3}}
        assert storage.save_index(index) is True
        loaded = storage.load_index()
        assert loaded["p1"]["events_count"] == 3
    finally:
        _cleanup(tmp)


def test_load_index_missing():
    tmp = _make_tmp_storage()
    try:
        loaded = storage.load_index()
        assert loaded == {}
    finally:
        _cleanup(tmp)
