import hashlib
import logging
import os
from datetime import date, datetime

from kivy.app import App
from kivy.utils import get_color_from_hex

LOG = logging.getLogger(__name__)

_PBKDF2_ITERATIONS = 600_000

def rgba_to_hex(rgba):
    r, g, b, a = rgba
    return "#{:02x}{:02x}{:02x}".format(
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )

def on_plant_seed(instance):
    app = App.get_running_app()
    app.previous_screen = app.screen.current
    app.screen.current = "sow_seed"

def go_to_garden(instance):
    app = App.get_running_app()
    garden = app.screen.get_screen("garden_view")
    garden.refresh_plants()
    app.previous_screen = app.screen.current
    app.screen.current = "garden_view"

def go_to_add_event(instance, plant):
    app = App.get_running_app()
    add_event_screen = app.screen.get_screen("add_event")
    add_event_screen.set_plant(plant)
    app.previous_screen = app.screen.current
    app.screen.current = "add_event"

def go_to_timeline(instance, plant):
    app = App.get_running_app()
    timeline_screen = app.screen.get_screen("timeline_view")
    # debug: dump timeline_screen type/attrs when troubleshooting missing methods
    try:
        print("DEBUG: timeline_screen type=", type(timeline_screen))
        print("DEBUG: timeline_screen dir sample=", dir(timeline_screen)[:80])
    except Exception:
        pass

    # best-effort: call set_plant if available; otherwise set plant_id and trigger update_timeline
    try:
        if hasattr(timeline_screen, 'set_plant'):
            timeline_screen.set_plant(plant)
        else:
            # fallback: set plant_id and call update_timeline if present
            pid = plant.get('id') if isinstance(plant, dict) else str(plant)
            if pid:
                try:
                    timeline_screen.plant_id = str(pid)
                except Exception:
                    pass
            if hasattr(timeline_screen, 'update_timeline'):
                try:
                    timeline_screen.update_timeline(pid)
                except Exception:
                    pass
    except Exception:
        # final fallback: ignore and let screen initialization handle it
        pass
    app.previous_screen = app.screen.current
    app.screen.current = "timeline_view"

def _coerce_to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None

        if "T" in value:
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value).date()
        return date.fromisoformat(value)
    return None


def get_difference_days(first_day, second_day):
    first = _coerce_to_date(first_day)
    second = _coerce_to_date(second_day)
    if first is None or second is None:
        return None
    delta = first - second
    return int(delta.days)


def parse_ts_to_datetime(ts_str):
    """Parse an ISO timestamp string to a datetime object."""
    if not ts_str:
        return None
    try:
        ts_str = ts_str.strip()
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str)
    except (ValueError, AttributeError):
        return None


# ---------------------------------------------------------------------------
# Password helpers (PBKDF2-HMAC-SHA256)
# ---------------------------------------------------------------------------

def hash_password(password: str) -> dict:
    """Hash a password for storage. Returns dict with salt, hash, enc_salt, iterations.

    Two independent PBKDF2 derivations are performed:
    1. Verification hash (stored for login comparison)
    2. Encryption salt (used to derive the AES key at unlock time)
    """
    verification_salt = os.urandom(16)
    enc_salt = os.urandom(16)

    verification_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), verification_salt, _PBKDF2_ITERATIONS
    )

    return {
        "salt": verification_salt.hex(),
        "hash": verification_hash.hex(),
        "enc_salt": enc_salt.hex(),
        "iterations": _PBKDF2_ITERATIONS,
    }


def verify_password(password: str, stored: dict) -> bool:
    """Verify a password against a stored hash dict.

    Uses hmac.compare_digest for constant-time comparison.
    """
    import hmac

    salt = bytes.fromhex(stored.get("salt", ""))
    expected = stored.get("hash", "")
    iterations = stored.get("iterations", _PBKDF2_ITERATIONS)

    derived = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(derived.hex(), expected)


def derive_encryption_key(password: str, stored: dict) -> bytes:
    """Derive the 32-byte AES-256 encryption key from the password and stored enc_salt."""
    enc_salt = bytes.fromhex(stored.get("enc_salt", ""))
    iterations = stored.get("iterations", _PBKDF2_ITERATIONS)

    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), enc_salt, iterations, dklen=32
    )