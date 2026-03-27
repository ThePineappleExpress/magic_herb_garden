"""Tests for photo_storage.py - blob I/O with temp directories."""

import json
import shutil
import tempfile
from pathlib import Path

import photo_storage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_original_photos_dir = photo_storage.PHOTOS_DIR
_original_photo_index = photo_storage.PHOTO_INDEX


def _make_tmp():
    tmp = Path(tempfile.mkdtemp(prefix="mht_photo_test_"))
    photo_storage.PHOTOS_DIR = tmp / "photos"
    photo_storage.PHOTO_INDEX = tmp / "photos_index.json"
    return tmp


def _cleanup(tmp):
    shutil.rmtree(tmp, ignore_errors=True)
    photo_storage.PHOTOS_DIR = _original_photos_dir
    photo_storage.PHOTO_INDEX = _original_photo_index


# ---------------------------------------------------------------------------
# save / load photo
# ---------------------------------------------------------------------------

def test_save_load_photo_roundtrip():
    tmp = _make_tmp()
    try:
        data = b"fake image data 12345"
        assert photo_storage.save_photo("plant1", "photo1", data) is True
        loaded = photo_storage.load_photo("plant1", "photo1")
        assert loaded == data
    finally:
        _cleanup(tmp)


def test_load_missing_photo_returns_none():
    tmp = _make_tmp()
    try:
        result = photo_storage.load_photo("noexist", "noexist")
        assert result is None
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# save / load thumbnail
# ---------------------------------------------------------------------------

def test_save_load_thumbnail_roundtrip():
    tmp = _make_tmp()
    try:
        data = b"fake thumbnail data"
        assert photo_storage.save_thumbnail("plant1", "photo1", data) is True
        loaded = photo_storage.load_thumbnail("plant1", "photo1")
        assert loaded == data
    finally:
        _cleanup(tmp)


def test_load_missing_thumbnail_returns_none():
    tmp = _make_tmp()
    try:
        result = photo_storage.load_thumbnail("noexist", "noexist")
        assert result is None
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# delete_photo
# ---------------------------------------------------------------------------

def test_delete_photo():
    tmp = _make_tmp()
    try:
        photo_storage.save_photo("plant1", "photo1", b"data")
        photo_storage.save_thumbnail("plant1", "photo1", b"thumb")
        assert photo_storage.delete_photo("plant1", "photo1") is True
        assert photo_storage.load_photo("plant1", "photo1") is None
        assert photo_storage.load_thumbnail("plant1", "photo1") is None
    finally:
        _cleanup(tmp)


def test_delete_photo_missing_noop():
    tmp = _make_tmp()
    try:
        # Should not raise
        result = photo_storage.delete_photo("noexist", "noexist")
        assert result is True
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# delete_plant_photos
# ---------------------------------------------------------------------------

def test_delete_plant_photos():
    tmp = _make_tmp()
    try:
        photo_storage.save_photo("plant1", "p1", b"data1")
        photo_storage.save_photo("plant1", "p2", b"data2")
        assert photo_storage.delete_plant_photos("plant1") is True
        assert photo_storage.load_photo("plant1", "p1") is None
        assert photo_storage.load_photo("plant1", "p2") is None
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# list_photo_files
# ---------------------------------------------------------------------------

def test_list_photo_files():
    tmp = _make_tmp()
    try:
        photo_storage.save_photo("plant1", "photo_a", b"data")
        photo_storage.save_photo("plant1", "photo_b", b"data")
        photo_storage.save_thumbnail("plant1", "photo_a", b"thumb")
        files = photo_storage.list_photo_files("plant1")
        assert "photo_a" in files
        assert "photo_b" in files
        # Thumbnails should not appear in the list
        assert all(".thumb" not in f for f in files)
    finally:
        _cleanup(tmp)


def test_list_photo_files_empty():
    tmp = _make_tmp()
    try:
        files = photo_storage.list_photo_files("noexist")
        assert files == []
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# photo index
# ---------------------------------------------------------------------------

def test_save_load_photo_index_roundtrip():
    tmp = _make_tmp()
    try:
        index = {
            "photo1": {"plant_id": "p1", "event_id": "e1", "garden_id": "g1", "mime": "image/jpeg"},
            "photo2": {"plant_id": "p1", "event_id": "e2", "garden_id": "g1", "mime": "image/png"},
        }
        assert photo_storage.save_photo_index(index) is True
        loaded = photo_storage.load_photo_index()
        assert loaded["photo1"]["mime"] == "image/jpeg"
        assert loaded["photo2"]["plant_id"] == "p1"
    finally:
        _cleanup(tmp)


def test_load_photo_index_missing():
    tmp = _make_tmp()
    try:
        loaded = photo_storage.load_photo_index()
        assert loaded == {}
    finally:
        _cleanup(tmp)


# ---------------------------------------------------------------------------
# save_photo creates directories
# ---------------------------------------------------------------------------

def test_save_photo_creates_dirs():
    tmp = _make_tmp()
    try:
        plant_dir = photo_storage.PHOTOS_DIR / "new_plant"
        assert not plant_dir.exists()
        photo_storage.save_photo("new_plant", "photo1", b"data")
        assert plant_dir.exists()
    finally:
        _cleanup(tmp)
