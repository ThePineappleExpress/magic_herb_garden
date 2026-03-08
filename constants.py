"""constants.py - Canonical event types and normalization."""

EVENT_WATERING = "watering"
EVENT_FEEDING = "feeding"
EVENT_LOG = "log"
EVENT_PLANTING = "planted"
EVENT_TOP = "top"
EVENT_PRUNE = "prune"
EVENT_FLIP = "flip"

_ALIASES = {
    "water": EVENT_WATERING,
    "watered": EVENT_WATERING,
    "feed": EVENT_FEEDING,
    "fed": EVENT_FEEDING,
    "note": EVENT_LOG,
    "notes": EVENT_LOG,
    "plant": EVENT_PLANTING,
    "planted": EVENT_PLANTING,
    "planting": EVENT_PLANTING,
    "topped": EVENT_TOP,
    "topping": EVENT_TOP,
    "pruned": EVENT_PRUNE,
    "pruning": EVENT_PRUNE,
    "flipped": EVENT_FLIP,
    "flipping": EVENT_FLIP,
}

ALL_EVENT_TYPES = (
    EVENT_WATERING,
    EVENT_FEEDING,
    EVENT_LOG,
    EVENT_PLANTING,
    EVENT_TOP,
    EVENT_PRUNE,
    EVENT_FLIP,
)


def normalize_event_type(raw: str) -> str:
    """Normalize an event type string to its canonical form.

    Returns the canonical type, or the lowered input if no alias matches.
    """
    lower = raw.strip().lower()
    if lower in ALL_EVENT_TYPES:
        return lower
    return _ALIASES.get(lower, lower)
