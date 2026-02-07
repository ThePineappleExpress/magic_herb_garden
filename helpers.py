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

def go_to_add_event(instance, plant):
    app = App.get_running_app()
    add_event_screen = app.screen.get_screen("add_event")
    add_event_screen.set_plant(plant)
    app.previous_screen = app.screen.current
    app.screen.current = "add_event"

def go_to_timeline(instance, plant):
    app = App.get_running_app()
    timeline_screen = app.screen.get_screen("timeline_view")
    # debug: dump timeline_screen type/attrs when troubleshooting missing methods
    try:
        print("DEBUG: timeline_screen type=", type(timeline_screen))
        print("DEBUG: timeline_screen dir sample=", dir(timeline_screen)[:80])
    except Exception:
        pass

    # best-effort: call set_plant if available; otherwise set plant_id and trigger update_timeline
    try:
        if hasattr(timeline_screen, 'set_plant'):
            timeline_screen.set_plant(plant)
        else:
            # fallback: set plant_id and call update_timeline if present
            pid = plant.get('id') if isinstance(plant, dict) else str(plant)
            if pid:
                try:
                    timeline_screen.plant_id = str(pid)
                except Exception:
                    pass
            if hasattr(timeline_screen, 'update_timeline'):
                try:
                    timeline_screen.update_timeline(pid)
                except Exception:
                    pass
    except Exception:
        # final fallback: ignore and let screen initialization handle it
        pass
    app.previous_screen = app.screen.current
    app.screen.current = "timeline_view"

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

        if "T" in value:
            if value.endswith("Z"):
                value = value[:-1] + "+00:00"
            return datetime.fromisoformat(value).date()
        return date.fromisoformat(value)
    return None


def get_difference_days(first_day, second_day):
    first = _coerce_to_date(first_day)
    second = _coerce_to_date(second_day)
    if first is None or second is None:
        return None
    delta = first - second
    return int(delta.days)