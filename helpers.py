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

