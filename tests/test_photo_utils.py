"""Tests for photo_utils.py - image processing helpers.

Requires Pillow to be installed.
"""

import io

from photo_utils import (
    pillow_available,
    validate_image,
    get_image_dimensions,
    get_mime_type,
    generate_thumbnail,
    process_image,
    THUMB_MAX_WIDTH,
    MAX_DIMENSION,
)


def _make_test_jpeg(width=100, height=100):
    """Create a minimal valid JPEG image in memory."""
    from PIL import Image
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _make_test_png(width=100, height=100):
    """Create a minimal valid PNG image in memory."""
    from PIL import Image
    img = Image.new("RGBA", (width, height), color=(0, 255, 0, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# pillow_available
# ---------------------------------------------------------------------------

def test_pillow_available():
    assert pillow_available() is True


# ---------------------------------------------------------------------------
# validate_image
# ---------------------------------------------------------------------------

def test_validate_image_valid_jpeg():
    data = _make_test_jpeg()
    assert validate_image(data) is True


def test_validate_image_valid_png():
    data = _make_test_png()
    assert validate_image(data) is True


def test_validate_image_invalid_bytes():
    assert validate_image(b"not an image at all") is False


def test_validate_image_empty():
    assert validate_image(b"") is False


def test_validate_image_none():
    assert validate_image(None) is False


def test_validate_image_too_large():
    """Images exceeding MAX_DIMENSION should fail validation."""
    data = _make_test_jpeg(MAX_DIMENSION + 1, 100)
    assert validate_image(data) is False


# ---------------------------------------------------------------------------
# get_image_dimensions
# ---------------------------------------------------------------------------

def test_get_image_dimensions_jpeg():
    data = _make_test_jpeg(640, 480)
    w, h = get_image_dimensions(data)
    assert w == 640 and h == 480


def test_get_image_dimensions_png():
    data = _make_test_png(200, 300)
    w, h = get_image_dimensions(data)
    assert w == 200 and h == 300


def test_get_image_dimensions_invalid():
    w, h = get_image_dimensions(b"garbage")
    assert w == 0 and h == 0


# ---------------------------------------------------------------------------
# get_mime_type
# ---------------------------------------------------------------------------

def test_get_mime_type_jpeg():
    data = _make_test_jpeg()
    assert get_mime_type(data) == "image/jpeg"


def test_get_mime_type_png():
    data = _make_test_png()
    assert get_mime_type(data) == "image/png"


def test_get_mime_type_invalid():
    assert get_mime_type(b"garbage") == "application/octet-stream"


# ---------------------------------------------------------------------------
# generate_thumbnail
# ---------------------------------------------------------------------------

def test_generate_thumbnail():
    data = _make_test_jpeg(800, 600)
    thumb = generate_thumbnail(data)
    assert isinstance(thumb, bytes)
    assert len(thumb) > 0
    assert len(thumb) < len(data), "Thumbnail should be smaller"


def test_generate_thumbnail_respects_max_width():
    data = _make_test_jpeg(1000, 800)
    thumb = generate_thumbnail(data)
    w, h = get_image_dimensions(thumb)
    assert w <= THUMB_MAX_WIDTH, f"Thumb width {w} exceeds max {THUMB_MAX_WIDTH}"


def test_generate_thumbnail_small_image_unchanged_width():
    """Images smaller than THUMB_MAX_WIDTH should not be upscaled."""
    data = _make_test_jpeg(100, 80)
    thumb = generate_thumbnail(data)
    w, h = get_image_dimensions(thumb)
    assert w <= 100


def test_generate_thumbnail_invalid_raises():
    try:
        generate_thumbnail(b"not an image")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# process_image
# ---------------------------------------------------------------------------

def test_process_image_jpeg():
    data = _make_test_jpeg(800, 600)
    result = process_image(data)
    assert result is not None
    assert result["format"] == "JPEG"
    assert result["mime"] == "image/jpeg"
    assert result["width"] == 800
    assert result["height"] == 600
    assert isinstance(result["thumb_bytes"], bytes)
    assert result["thumb_width"] <= THUMB_MAX_WIDTH


def test_process_image_png():
    data = _make_test_png(200, 150)
    result = process_image(data)
    assert result is not None
    assert result["format"] == "PNG"
    assert result["mime"] == "image/png"
    assert result["width"] == 200
    assert result["height"] == 150


def test_process_image_invalid():
    result = process_image(b"not an image")
    assert result is None


def test_process_image_empty():
    result = process_image(b"")
    assert result is None


def test_process_image_none():
    result = process_image(None)
    assert result is None


def test_process_image_too_large():
    data = _make_test_jpeg(MAX_DIMENSION + 1, 100)
    result = process_image(data)
    assert result is None
