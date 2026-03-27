"""plant_service.py - Plant lifecycle: create, update, side-effects.

Pure logic extracted from set_environment.py and add_event.py.
No Kivy imports.
"""

import logging
from datetime import date

from data import PlantRepository
from constants import EVENT_TOP, EVENT_PRUNE, EVENT_FLIP, EVENT_HARVEST

LOG = logging.getLogger(__name__)


def create_plant(garden_id: str, plant: dict) -> bool:
    """Add a new plant to *garden_id* via PlantRepository.

    Returns True on success.  The caller is responsible for populating
    the plant dict with all required fields (id, strain, etc.).
    """
    if not garden_id:
        LOG.error("create_plant called with no garden_id")
        return False
    return PlantRepository.add(garden_id, plant)


def apply_event_side_effects(
    garden_id: str,
    plant_id: str,
    event_type: str,
) -> bool:
    """Update the plant record after special event types.

    Side-effects:
    - top / prune: adds 7 penalty days to harvest estimate
    - flip: sets flip_date + stage='flowering'
    - harvest: sets harvest_date + stage='harvested'

    Returns True if the plant was successfully updated, False otherwise.
    """
    if not garden_id or not plant_id:
        LOG.error("apply_event_side_effects: missing garden_id or plant_id")
        return False

    plant = PlantRepository.get(garden_id, plant_id)
    if plant is None:
        LOG.error("Plant %s not found in garden %s", plant_id, garden_id)
        return False

    changed = False

    if event_type in (EVENT_TOP, EVENT_PRUNE):
        penalty = int(plant.get("penalty", 0) or 0)
        plant["penalty"] = penalty + 7
        changed = True

    if event_type == EVENT_FLIP:
        plant["flip_date"] = date.today().isoformat()
        plant["stage"] = "flowering"
        changed = True

    if event_type == EVENT_HARVEST:
        plant["harvest_date"] = date.today().isoformat()
        plant["stage"] = "harvested"
        changed = True

    if changed:
        ok = PlantRepository.update(garden_id, plant_id, plant)
        if ok:
            LOG.info("Side-effects applied for %s on plant %s", event_type, plant_id)
        else:
            LOG.error("Failed to save side-effects for %s on plant %s", event_type, plant_id)
        return ok

    return True  # nothing to change is not an error
