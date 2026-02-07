import json, os, random
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

    with DB_PATH.open("r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        data = json.loads(content)
        return _normalize_plants(data)


def save_plants(plants):  # Save plant data to JSON file
    normalized = _normalize_plants(plants)
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2)


def save_plant(plant):  # Save a single plant entry to the JSON file
    plants = load_plants()
    if isinstance(plant, dict):
        plants.append(plant)
    save_plants(plants)
    # Create events file with correct structure
    plant_id = plant.get("id")
    date_planted = plant.get("date_planted", datetime.now().strftime("%Y-%m-%d"))
    initial_event = {
        'id': 'evt-0',
        'ts': date_planted,
        'type': 'planted',
        'volume_l': 0.1,
        'water_temp_c': 18,
        'ph': 5.8,
        'ppm': 140,
        'feeding': {
            'grow_mix': 0.0,
            'root_mix': 0.0,
            'bloom_mix': 0.0,
            'bloom_boost': 0.0,
            'soil_boost': 0.0,
            'vit_boost': 0.0,
            'CalMag': 0.0,
            'myco_trico': False
        },
        'plant': {
            'stage': 'planting',
            'plant_height': 0,
            'num_nodes': 0,
            'node_spacing': 0,
            'main_stem_number': 1,
            'leaf_color': 'light',
            'leaf_morphology': 'normal',
            'deficiencies': {k: False for k in ['n','p','k','ca','mg','s','fe','mn','zn','cu','b','mo']},
            'excess': {k: False for k in ['n','p','k','ca','mg','s','fe','mn','zn','cu','b','mo']}
        },
        'environment': {
            'air_temp_c': 20,
            'rh_percent': 55,
            'soil_moisture': 'wet',
            'soil_ph': 5.5,
            'vpd_kpa': 1.1,
            'ppfd': 100,
            'light_schedule': [18, 6]
        },
        'notes': f"Planted {plant['strain']} from {plant['name']} on {date_planted}."
    }
    events_data = {
        'plant_id': plant_id,
        'penalty': 0,
        'events': [initial_event]
    }
    events_path = os.path.join(EVENTS_DIR, f"{plant_id}.json")
    with open(events_path, 'w') as f:
        json.dump(events_data, f, indent=2)
    print(f"Added plant {plant['strain']} ({plant_id}) and created events file.")


def load_plant_events(plant_id: str):
    path = os.path.join(EVENTS_DIR, f"{plant_id}.json")
    if not os.path.exists(path):
        return None  # or {} / {"events": []}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

