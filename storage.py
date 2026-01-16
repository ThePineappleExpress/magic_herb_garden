import json
from pathlib import Path

DB_PATH = Path("usr/db/plants.json")


def load_plants():
    if not DB_PATH.exists():
        return []
    try:
        with DB_PATH.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_plant(plant):
    plants = load_plants()
    plants.append(plant)
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(plants, f, indent=2)