"""Tests for weed_format.py - .weed binary export/import.

Uses tempfile for isolated file I/O.
"""

import json
import os
import tempfile
import shutil
from pathlib import Path

from weed_format import (
    write_weed,
    read_weed,
    WeedPasswordRequired,
    WeedWrongPassword,
    WeedCorrupted,
    WEED_MAGIC,
    WEED_VERSION,
)


def _make_gardens_data(num_gardens=1, num_plants=1, num_events=2):
    """Build a test data structure for write_weed."""
    gardens_data = []
    for gi in range(num_gardens):
        plants = []
        events = {}
        for pi in range(num_plants):
            pid = f"plant-{gi}-{pi}"
            plants.append({"id": pid, "strain": f"Strain {pi}", "status": "active"})
            event_list = []
            for ei in range(num_events):
                event_list.append({
                    "id": f"evt-{gi}-{pi}-{ei}",
                    "ts": f"2025-01-{ei+1:02d}T10:00:00",
                    "type": "watering" if ei % 2 == 0 else "feeding",
                    "notes": f"Event {ei}",
                })
            events[pid] = {"plant_id": pid, "penalty": 0, "events": event_list}
        garden = {
            "id": f"garden-{gi}",
            "name": f"Garden {gi}",
            "type": "indoor",
            "plants": plants,
        }
        gardens_data.append({"garden": garden, "events": events})
    return gardens_data


def _tmpdir():
    return tempfile.mkdtemp(prefix="mht_weed_test_")


# ---------------------------------------------------------------------------
# Roundtrip: unencrypted
# ---------------------------------------------------------------------------

def test_write_read_roundtrip():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "test.weed"
        data = _make_gardens_data(1, 2, 3)
        write_weed(path, data, include_photos=False)
        result = read_weed(path)

        assert result["encrypted"] is False
        assert result["manifest"] is not None
        assert len(result["gardens"]) == 1
        assert result["gardens"][0]["name"] == "Garden 0"
        assert len(result["gardens"][0]["plants"]) == 2
        # Check events were included
        assert len(result["events"]) == 2  # 2 plants
    finally:
        shutil.rmtree(tmp)


def test_roundtrip_multiple_gardens():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "multi.weed"
        data = _make_gardens_data(3, 1, 2)
        write_weed(path, data, include_photos=False)
        result = read_weed(path)

        assert len(result["gardens"]) == 3
        names = {g["name"] for g in result["gardens"]}
        assert "Garden 0" in names
        assert "Garden 1" in names
        assert "Garden 2" in names
    finally:
        shutil.rmtree(tmp)


def test_roundtrip_empty_gardens():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "empty.weed"
        write_weed(path, [], include_photos=False)
        result = read_weed(path)

        assert result["manifest"] is not None
        assert result["gardens"] == []
        assert result["events"] == {}
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Roundtrip: password-protected
# ---------------------------------------------------------------------------

def test_write_read_with_password():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "encrypted.weed"
        data = _make_gardens_data(1, 1, 2)
        write_weed(path, data, export_password="secret123", include_photos=False)
        result = read_weed(path, export_password="secret123")

        assert result["encrypted"] is True
        assert len(result["gardens"]) == 1
        assert result["gardens"][0]["name"] == "Garden 0"
    finally:
        shutil.rmtree(tmp)


def test_read_password_required_raises():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "encrypted.weed"
        data = _make_gardens_data(1, 1, 1)
        write_weed(path, data, export_password="mypass", include_photos=False)
        try:
            read_weed(path)  # no password
            assert False, "Should have raised WeedPasswordRequired"
        except WeedPasswordRequired:
            pass
    finally:
        shutil.rmtree(tmp)


def test_read_wrong_password_raises():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "encrypted.weed"
        data = _make_gardens_data(1, 1, 1)
        write_weed(path, data, export_password="correct", include_photos=False)
        try:
            read_weed(path, export_password="wrong")
            assert False, "Should have raised WeedWrongPassword"
        except WeedWrongPassword:
            pass
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Corruption detection
# ---------------------------------------------------------------------------

def test_read_corrupted_file():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "corrupt.weed"
        path.write_bytes(b"some random garbage data that is not a weed file at all")
        try:
            read_weed(path)
            assert False, "Should have raised WeedCorrupted"
        except WeedCorrupted:
            pass
    finally:
        shutil.rmtree(tmp)


def test_read_truncated_file():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "truncated.weed"
        path.write_bytes(b"WEED\x02")
        try:
            read_weed(path)
            assert False, "Should have raised WeedCorrupted"
        except WeedCorrupted:
            pass
    finally:
        shutil.rmtree(tmp)


def test_read_tampered_hmac():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "tampered.weed"
        data = _make_gardens_data(1, 1, 1)
        write_weed(path, data, include_photos=False)

        # Read and tamper with the last byte of the HMAC
        raw = bytearray(path.read_bytes())
        raw[-1] ^= 0xFF  # flip bits
        path.write_bytes(bytes(raw))

        try:
            read_weed(path)
            assert False, "Should have raised WeedCorrupted"
        except WeedCorrupted:
            pass
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Manifest content
# ---------------------------------------------------------------------------

def test_manifest_contains_expected_fields():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "manifest.weed"
        data = _make_gardens_data(2, 3, 4)
        write_weed(path, data, include_photos=False)
        result = read_weed(path)

        manifest = result["manifest"]
        assert "export_date" in manifest
        assert "app_version" in manifest
        assert manifest["garden_count"] == 2
        assert len(manifest["garden_ids"]) == 2
    finally:
        shutil.rmtree(tmp)


# ---------------------------------------------------------------------------
# Events data integrity
# ---------------------------------------------------------------------------

def test_events_roundtrip_data_integrity():
    tmp = _tmpdir()
    try:
        path = Path(tmp) / "integrity.weed"
        data = _make_gardens_data(1, 1, 5)
        write_weed(path, data, include_photos=False)
        result = read_weed(path)

        # Check that events were preserved
        for plant_id, ev_data in result["events"].items():
            events = ev_data.get("events", [])
            assert len(events) == 5, f"Expected 5 events, got {len(events)}"
    finally:
        shutil.rmtree(tmp)
