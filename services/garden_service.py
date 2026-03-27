"""garden_service.py - Garden plant views, filtering, and sorting.

Pure logic extracted from garden_view.py.  No Kivy imports.
"""

import logging
from datetime import date, datetime

from data import PlantRepository, IndexRepository

LOG = logging.getLogger(__name__)


def _coerce_to_date(value) -> date | None:
    """Coerce a string or date/datetime to a date object."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        value = value.strip()
        try:
            if "T" in value:
                if value.endswith("Z"):
                    value = value[:-1] + "+00:00"
                return datetime.fromisoformat(value).date()
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            return None
    return None


def _difference_days(first, second) -> int | None:
    """Return (first - second) in days, or None if either can't be parsed."""
    a = _coerce_to_date(first)
    b = _coerce_to_date(second)
    if a is None or b is None:
        return None
    return (a - b).days


def get_garden_plants_view(garden_id: str, today: date | None = None) -> list[dict]:
    """Build the display-ready plant list for a garden.

    Each returned dict contains plant metadata plus computed fields:
    ``last_watering``, ``flower_status``, ``harvest_status``.

    Returns an empty list when *garden_id* is None or the garden doesn't exist.
    """
    if not garden_id:
        return []
    today = today or date.today()
    plants = PlantRepository.list_for_garden(garden_id)
    index = IndexRepository.get_all()

    data: list[dict] = []
    for p in plants:
        if not isinstance(p, dict):
            continue
        plant_id = p.get("id")
        name = p.get("seedbank") or p.get("name", "")
        strain = p.get("strain", "")
        notes = p.get("notes", "")
        genes = p.get("genes", "")
        date_planted = p.get("date_planted", "")

        idx_entry = index.get(str(plant_id), {}) if plant_id else {}
        last_event_ts = idx_entry.get("last_event_ts")

        last_watering = _difference_days(today, last_event_ts) if last_event_ts else None
        last_watering_str = str(last_watering) if last_watering is not None else "-"

        next_watering = "-"
        flower_status = "-"
        harvest_status = "-"

        # Compute flower / harvest estimates
        dt_str = p.get("date_planted")
        base_f = p.get("days_to_flower")
        try:
            base_f = int(base_f) if base_f is not None else 0
        except (ValueError, TypeError):
            base_f = 0
        penalty = int(p.get("penalty", 0) or 0)
        est_f = base_f + 14 + penalty
        est_h = est_f * 2

        if dt_str and est_h:
            try:
                y, m, d = map(int, dt_str.split("-"))
                planted = date(y, m, d)
                days_since = (today - planted).days
                days_left = est_h - days_since
                harvest_status = str(days_left) if days_left >= 0 else "harvested"
            except Exception:
                harvest_status = str(est_h)

        if dt_str and est_f:
            try:
                y, m, d = map(int, dt_str.split("-"))
                planted = date(y, m, d)
                days_since = (today - planted).days
                days_left = est_f - days_since
                if days_left > 0:
                    flower_status = str(days_left)
                elif harvest_status != "harvested":
                    flower_status = "flowering"
                else:
                    flower_status = "harvested"
            except Exception:
                flower_status = str(est_f)

        stage = p.get("stage", "")
        if stage == "harvested":
            harvest_status = "harvested"
            flower_status = "harvested"
        elif stage == "flowering":
            if flower_status not in ("flowering", "harvested"):
                flower_status = "flowering"

        data.append({
            "id": plant_id,
            "genes": genes,
            "seedbank": name,
            "strain": strain,
            "notes": notes,
            "medium": p.get("medium"),
            "last_watering": last_watering_str,
            "next_watering": next_watering,
            "flower_status": flower_status,
            "harvest_status": harvest_status,
            "date_planted": date_planted,
        })

    return data


def filter_plants(
    items: list[dict],
    search_text: str = "",
    active_only: bool = False,
    harvested_label: str = "harvested",
) -> list[dict]:
    """Filter a plant view list by search text and active-only flag.

    *harvested_label* is the locale-specific string for "harvested" status,
    so callers can pass ``lang.STATUS_HARVESTED`` without this module
    importing lang directly.
    """
    result = list(items)

    if search_text:
        q = search_text.lower()
        result = [
            p for p in result
            if q in (p.get("strain") or "").lower()
            or q in (p.get("seedbank") or "").lower()
            or q in (p.get("notes") or "").lower()
            or q in (p.get("medium") or "").lower()
            or q in (p.get("genes") or "").lower()
        ]

    if active_only:
        result = [
            p for p in result
            if p.get("harvest_status") != harvested_label
        ]

    return result


def sort_plants(
    items: list[dict],
    key: str = "strain",
    ascending: bool = True,
) -> list[dict]:
    """Sort a plant view list by *key*."""

    def sort_val(p):
        v = p.get(key) or ""
        if isinstance(v, str):
            try:
                return (0, float(v))
            except (ValueError, TypeError):
                return (1, v.lower())
        return (1, str(v).lower())

    return sorted(items, key=sort_val, reverse=not ascending)
