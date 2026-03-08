"""validators.py - JSON schema definitions for plants, events, gardens.

Graceful no-op if jsonschema is not installed.
"""

import logging

LOG = logging.getLogger(__name__)

try:
    from jsonschema import validate, ValidationError
    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

PLANT_SCHEMA = {
    "type": "object",
    "required": ["id", "strain"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "strain": {"type": "string"},
        "seedbank": {"type": "string"},
        "genes": {"type": "string"},
        "type": {"type": "string"},
        "notes": {"type": "string"},
        "medium": {"type": "string"},
        "date_planted": {"type": "string"},
        "days_to_flower": {"type": ["integer", "string"]},
        "status": {"type": "string"},
    },
}

EVENT_SCHEMA = {
    "type": "object",
    "required": ["id", "ts", "type"],
    "properties": {
        "id": {"type": "string"},
        "ts": {"type": "string"},
        "type": {"type": "string"},
    },
}

GARDEN_SCHEMA = {
    "type": "object",
    "required": ["id", "name"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "plants": {"type": "array"},
        "created_at": {"type": "string"},
    },
}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_plant(data: dict) -> bool:
    """Return True if *data* matches the plant schema."""
    if not _HAS_JSONSCHEMA:
        return True
    try:
        validate(instance=data, schema=PLANT_SCHEMA)
        return True
    except ValidationError as exc:
        LOG.warning("Plant validation failed: %s", exc.message)
        return False


def validate_event(data: dict) -> bool:
    """Return True if *data* matches the event schema."""
    if not _HAS_JSONSCHEMA:
        return True
    try:
        validate(instance=data, schema=EVENT_SCHEMA)
        return True
    except ValidationError as exc:
        LOG.warning("Event validation failed: %s", exc.message)
        return False


def validate_garden(data: dict) -> bool:
    """Return True if *data* matches the garden schema."""
    if not _HAS_JSONSCHEMA:
        return True
    try:
        validate(instance=data, schema=GARDEN_SCHEMA)
        return True
    except ValidationError as exc:
        LOG.warning("Garden validation failed: %s", exc.message)
        return False
