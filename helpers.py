from datetime import date, datetime
from kivy.app import App

from kivy.utils import get_color_from_hex

def rgba_to_hex(rgba):
    r, g, b, a = rgba
    return "#{:02x}{:02x}{:02x}".format(
        int(r * 255),
        int(g * 255),
        int(b * 255),
    )

def on_plant_seed(instance):
    app = App.get_running_app()
    app.previous_screen = app.screen.current
    app.screen.current = "sow_seed"

def go_to_garden(instance):
    app = App.get_running_app()
    garden = app.screen.get_screen("garden_view")
    garden.refresh_plants()
    app.previous_screen = app.screen.current
    app.screen.current = "garden_view"

def _coerce_to_date(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            if "T" in value:
                if value.endswith("Z"):
                    value = value[:-1] + "+00:00"
                return datetime.fromisoformat(value).date()
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def get_difference_days(first_day, second_day):
    first = _coerce_to_date(first_day)
    second = _coerce_to_date(second_day)
    if first is None or second is None:
        return None
    delta = first - second
    return int(delta.days)