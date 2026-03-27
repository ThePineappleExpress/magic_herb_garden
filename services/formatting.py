"""formatting.py - Display formatting helpers (relative time, health).

Extracted from plant_details.py.  No Kivy imports.
"""


def get_nutrient_status(plant: dict, key: str) -> str | None:
    """Check a single nutrient for deficiency or excess.

    Returns ``"deficient"``, ``"excess"``, or ``None`` (healthy).
    """
    deficiencies = plant.get("deficiencies", {})
    excess = plant.get("excess", {})
    if deficiencies.get(key):
        return "deficient"
    if excess.get(key):
        return "excess"
    return None


_NUTRIENTS = ("n", "p", "k", "ca", "mg", "s", "fe", "mn", "zn", "cu", "b", "mo")


def get_health_indicator(plant: dict) -> str:
    """Return a human-readable health summary for a plant.

    Returns one of: ``"Healthy"``, ``"Minor issues"``,
    ``"Moderate issues"``, or ``"Severe issues"``.
    """
    indicators: list[str] = []
    coloration = plant.get("leaf_color", "normal")
    morphology = plant.get("leaf_morphology", "normal")

    for nutrient in _NUTRIENTS:
        status = get_nutrient_status(plant, nutrient)
        if status == "deficient":
            indicators.append(f"{nutrient.upper()}↓")
        elif status == "excess":
            indicators.append(f"{nutrient.upper()}↑")

    if len(indicators) == 0 and coloration == "normal" and morphology == "normal":
        return "Healthy"
    elif len(indicators) > 3 and coloration != "normal" and morphology != "normal":
        return "Severe issues"
    elif len(indicators) > 3 and (coloration != "normal" or morphology == "normal"):
        return "Moderate issues"
    elif len(indicators) <= 3 and coloration == "normal" and morphology == "normal":
        return "Minor issues"
    else:
        return "Minor issues"


def format_relative_time(days: int | None) -> str:
    """Format a days-ago count into a short human-readable string.

    Examples: ``"today"``, ``"1 day ago"``, ``"14 days ago"``.
    Returns ``"-"`` for None.
    """
    if days is None:
        return "-"
    if days == 0:
        return "today"
    if days == 1:
        return "1 day ago"
    return f"{days} days ago"
