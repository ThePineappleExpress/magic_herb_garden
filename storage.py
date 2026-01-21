import json, os
from uuid import uuid4
from datetime import datetime
from pathlib import Path

DB_PATH = Path("usr/db/plants.json")
EVENTS_DIR = os.path.join(os.path.dirname(__file__), "usr", "db", "plants")




def _normalize_plants(data):    # Normalize plant data into a list of dictionaries
    if data is None:
        return []
    if isinstance(data, dict):
        return [data]
    if not isinstance(data, list):
        return []

    normalized = []
    for item in data:
        if isinstance(item, dict):
            normalized.append(item)
        elif isinstance(item, list):
            for sub in item:
                if isinstance(sub, dict):
                    normalized.append(sub)
    return normalized


def load_plants():  # Load plant data from JSON file
    if not DB_PATH.exists():
        return []
    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            data = json.loads(content)
            return _normalize_plants(data)
    except json.JSONDecodeError:
        return []


def save_plants(plants):  # Save plant data to JSON file
    normalized = _normalize_plants(plants)
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)


def save_plant(plant):  # Save a single plant entry to the JSON file
    plants = load_plants()
    if isinstance(plant, dict):
        plants.append(plant)
    save_plants(plants)

def load_plant_events(plant_id: str):
    path = os.path.join(EVENTS_DIR, f"{plant_id}.json")
    if not os.path.exists(path):
        return None  # or {} / {"events": []}
    with open(path, "r", encoding="utf-8") as f:
        print("load successful")
        return json.load(f)

def load_events(self):
    self.events_container.clear_widgets()

    plant = self.plant or {}
    plant_id = plant.get("id") or plant.get("plant_id")
    print("details: plant_id:", repr(plant_id))

    path = os.path.join(EVENTS_DIR, f"{plant_id}.json")
    print("looking for:", path, "exists:", os.path.exists(path))

    data = load_plant_events(str(plant_id))
    if not data or not data.get("events"):
        return

    events = data["events"]
    return events