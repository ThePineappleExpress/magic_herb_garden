"""photo_utils.py - Image processing helpers for photo attachments.

Uses Pillow for thumbnail generation, validation, and metadata extraction.
"""

import io
import logging

LOG = logging.getLogger(__name__)

THUMB_MAX_WIDTH = 320
THUMB_QUALITY = 80
MAX_DIMENSION = 4096

try:
    from PIL import Image, ExifTags
    _HAS_PILLOW = True
except ImportError:
    _HAS_PILLOW = False
    LOG.warning("Pillow not installed - photo features disabled")


def pillow_available() -> bool:
    return _HAS_PILLOW


def validate_image(image_bytes: bytes) -> bool:
    """Return True if bytes are a valid JPEG/PNG within MAX_DIMENSION."""
    if not _HAS_PILLOW or not image_bytes:
        return False
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        if img.format not in ("JPEG", "PNG"):
            return False
        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            return False
        return True
    except Exception:
        return False


def get_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
    """Return (width, height) without fully decoding the image."""
    if not _HAS_PILLOW:
        return (0, 0)
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return (img.width, img.height)
    except Exception:
        return (0, 0)


def get_mime_type(image_bytes: bytes) -> str:
    """Return 'image/jpeg' or 'image/png' from Pillow detection."""
    if not _HAS_PILLOW:
        return "application/octet-stream"
    try:
        img = Image.open(io.BytesIO(image_bytes))
        fmt = img.format
        if fmt == "JPEG":
            return "image/jpeg"
        elif fmt == "PNG":
            return "image/png"
        return "application/octet-stream"
    except Exception:
        return "application/octet-stream"


def _fix_exif_orientation(img):
    """Transpose image based on EXIF orientation tag."""
    try:
        exif = img.getexif()
        orientation_key = None
        for tag, name in ExifTags.TAGS.items():
            if name == "Orientation":
                orientation_key = tag
                break
        if orientation_key is None or orientation_key not in exif:
            return img
        orientation = exif[orientation_key]
        transforms = {
            2: Image.FLIP_LEFT_RIGHT,
            3: Image.ROTATE_180,
            4: Image.FLIP_TOP_BOTTOM,
            5: Image.TRANSPOSE,
            6: Image.ROTATE_270,
            7: Image.TRANSVERSE,
            8: Image.ROTATE_90,
        }
        if orientation in transforms:
            img = img.transpose(transforms[orientation])
    except Exception:
        pass
    return img


def generate_thumbnail(image_bytes: bytes) -> bytes:
    """Return JPEG thumbnail bytes (max 320px wide, aspect-preserved).

    Fixes EXIF orientation and strips EXIF metadata.
    Raises ValueError if image cannot be decoded.
    """
    if not _HAS_PILLOW:
        raise ValueError("Pillow not available")
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = _fix_exif_orientation(img)

        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        w, h = img.size
        if w > THUMB_MAX_WIDTH:
            ratio = THUMB_MAX_WIDTH / w
            new_w = THUMB_MAX_WIDTH
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=THUMB_QUALITY, optimize=True)
        return buf.getvalue()
    except Exception as exc:
        raise ValueError(f"Failed to generate thumbnail: {exc}") from exc


def process_image(image_bytes: bytes) -> dict | None:
    """Validate, extract metadata, and generate thumbnail in a single decode pass.

    Returns dict with keys: format, mime, width, height, thumb_bytes, thumb_width, thumb_height.
    Returns None if validation fails.
    """
    if not _HAS_PILLOW or not image_bytes:
        return None
    try:
        buf = io.BytesIO(image_bytes)
        img = Image.open(buf)
        fmt = img.format
        w, h = img.size

        # Validate format and dimensions
        if fmt not in ("JPEG", "PNG"):
            return None
        if w > MAX_DIMENSION or h > MAX_DIMENSION:
            return None

        # verify() checks CRC/structure — consumes the file pointer
        img.verify()
        buf.seek(0)
        img = Image.open(buf)

        # MIME type
        mime = "image/jpeg" if fmt == "JPEG" else ("image/png" if fmt == "PNG" else "application/octet-stream")

        # Thumbnail generation
        img = _fix_exif_orientation(img)
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        tw, th = img.size
        if tw > THUMB_MAX_WIDTH:
            ratio = THUMB_MAX_WIDTH / tw
            tw = THUMB_MAX_WIDTH
            th = int(th * ratio)
            img = img.resize((tw, th), Image.LANCZOS)
        else:
            tw, th = img.size

        thumb_buf = io.BytesIO()
        img.save(thumb_buf, format="JPEG", quality=THUMB_QUALITY, optimize=True)
        thumb_bytes = thumb_buf.getvalue()

        return {
            "format": fmt,
            "mime": mime,
            "width": w,
            "height": h,
            "thumb_bytes": thumb_bytes,
            "thumb_width": tw,
            "thumb_height": th,
        }
    except Exception:
        LOG.exception("process_image failed")
        return None