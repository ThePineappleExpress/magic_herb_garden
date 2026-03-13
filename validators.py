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
        "seedbank": {"type": "string"},
        "strain": {"type": "string"},
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
        "photos": {"type": "array", "items": {"type": "string"}},
    },
}

PHOTO_INDEX_ENTRY_SCHEMA = {
    "type": "object",
    "required": ["plant_id", "event_id", "garden_id", "mime"],
    "properties": {
        "plant_id":      {"type": "string"},
        "event_id":      {"type": "string"},
        "garden_id":     {"type": "string"},
        "original_name": {"type": "string"},
        "mime":          {"type": "string"},
        "width":         {"type": "integer"},
        "height":        {"type": "integer"},
        "thumb_width":   {"type": "integer"},
        "thumb_height":  {"type": "integer"},
        "size_bytes":    {"type": "integer"},
        "added_ts":      {"type": "string"},
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


# ---------------------------------------------------------------------------
# Error-list validators (return list[str] instead of bool)
# ---------------------------------------------------------------------------

def check_plant(data: dict) -> list[str]:
    """Validate *data* against the plant schema, returning a list of errors.

    Returns an empty list when the data is valid.  Falls back to basic
    structural checks when jsonschema is not installed.
    """
    if not isinstance(data, dict):
        return ["Plant data must be a dict"]
    if not _HAS_JSONSCHEMA:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        if not data.get("strain"):
            errors.append("Missing required field: strain")
        return errors
    from jsonschema import Draft7Validator
    v = Draft7Validator(PLANT_SCHEMA)
    return [e.message for e in sorted(v.iter_errors(data), key=lambda e: list(e.path))]


def check_event(data: dict) -> list[str]:
    """Validate *data* against the event schema, returning a list of errors.

    Returns an empty list when the data is valid.  Falls back to basic
    structural checks when jsonschema is not installed.
    """
    if not isinstance(data, dict):
        return ["Event data must be a dict"]
    if not _HAS_JSONSCHEMA:
        errors = []
        for field in ("id", "ts", "type"):
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        return errors
    from jsonschema import Draft7Validator
    v = Draft7Validator(EVENT_SCHEMA)
    return [e.message for e in sorted(v.iter_errors(data), key=lambda e: list(e.path))]


def check_garden(data: dict) -> list[str]:
    """Validate *data* against the garden schema, returning a list of errors.

    Returns an empty list when the data is valid.  Falls back to basic
    structural checks when jsonschema is not installed.
    """
    if not isinstance(data, dict):
        return ["Garden data must be a dict"]
    if not _HAS_JSONSCHEMA:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        if not data.get("name"):
            errors.append("Missing required field: name")
        return errors
    from jsonschema import Draft7Validator
    v = Draft7Validator(GARDEN_SCHEMA)
    return [e.message for e in sorted(v.iter_errors(data), key=lambda e: list(e.path))]
