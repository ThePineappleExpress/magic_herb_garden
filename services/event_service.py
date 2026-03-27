"""event_service.py - Event CRUD wrappers and sorted loading.

No Kivy imports.
"""

import logging

from data import EventRepository

LOG = logging.getLogger(__name__)


def get_events_sorted(plant_id: str, reverse: bool = True) -> list[dict]:
    """Return events for *plant_id* sorted by timestamp.

    *reverse=True* gives newest-first (default for timeline display).
    Returns an empty list if the plant has no events.
    """
    data = EventRepository.get(plant_id)
    if data is None:
        return []
    events = data.get("events", [])
    if not isinstance(events, list):
        return []

    def _sort_key(ev):
        return ev.get("ts", "") if isinstance(ev, dict) else ""

    return sorted(events, key=_sort_key, reverse=reverse)


def add_event(plant_id: str, event: dict) -> bool:
    """Append an event to a plant's event log via EventRepository.

    Returns True on success.
    """
    return EventRepository.add_event(plant_id, event)
