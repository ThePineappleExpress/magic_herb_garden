import logging

from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
from kivy.clock import Clock

from bin.themes import load_theme, apply_theme, get_default_theme, get_shader_colors
from data import SettingsRepository, GardenRepository
import lang

LOG = logging.getLogger(__name__)

# initial window size
Config.set("graphics", "width", "1920")
Config.set("graphics", "height", "1080")
Config.set("graphics", "resizable", "1")

# minimum size
Config.set("graphics", "minimum_width", "800")
Config.set("graphics", "minimum_height", "600")

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class MagicHerbTracker(App):
    theme = ObjectProperty(None)
    previous_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wizard_data = {}
        self.current_garden_id = None
        self.post_unlock_screen = None

    def build(self):
        self.theme = Factory.Theme()
        self.screen = ScreenManager(transition=FadeTransition(duration=0.1))
        Window.size = (1920, 1080)

        # Apply saved theme
        settings = SettingsRepository.get_all()
        theme_name = settings.get("theme", get_default_theme())
        theme_data = load_theme(theme_name)
        apply_theme(self.theme, theme_data)

        # Bootstrap: determine which screens are needed for first frame
        has_password = bool(settings.get("password"))
        gardens = GardenRepository.list_all()

        # Build only the screens needed for the initial route
        bootstrap_screens = set()
        if has_password:
            bootstrap_screens.add("password_check")
            if len(gardens) == 1:
                self.current_garden_id = gardens[0].get("id")
                self.post_unlock_screen = "garden_view"
            elif len(gardens) > 1:
                self.post_unlock_screen = "select_garden"
            else:
                self.post_unlock_screen = "select_garden"
            initial_screen = "password_check"
        elif len(gardens) == 1:
            self.current_garden_id = gardens[0].get("id")
            bootstrap_screens.add("garden_view")
            initial_screen = "garden_view"
        elif len(gardens) > 1:
            bootstrap_screens.add("select_garden")
            initial_screen = "select_garden"
        else:
            bootstrap_screens.add("empty_garden")
            initial_screen = "empty_garden"

        # Register bootstrap screens eagerly
        for name in bootstrap_screens:
            self.screen.add_widget(self._create_screen(name))

        # Push shader colors to bootstrap screens
        shader_name = settings.get("shader")
        color_a, color_b = get_shader_colors(theme_data, shader_name)
        for scr in self.screen.screens:
            if hasattr(scr, 'update_shader_colors'):
                scr.update_shader_colors(color_a, color_b)

        self.screen.current = initial_screen

        # Defer remaining screens - build in background after first frame
        Clock.schedule_once(lambda dt: self._build_remaining_screens(
            bootstrap_screens, color_a, color_b), 0.3)

        return self.screen

    # Screen name → (module, class) mapping
    _SCREEN_REGISTRY = {
        "empty_garden":    ("empty_garden",         "EmptyGardenScreen"),
        "sow_seed":        ("sow_seed",             "SowSeedScreen"),
        "set_environment": ("set_environment",       "SetEnvironmentScreen"),
        "plant_details":   ("plant_details",         "PlantDetailsScreen"),
        "garden_view":     ("garden_view",           "GardenViewScreen"),
        "are_you_sure":    ("are_you_sure",          "AreYouSure"),
        "add_event":       ("add_event",             "AddEventScreen"),
        "timeline_view":   ("timeline_view",         "TimelineScreen"),
        "password_check":  ("password_check",        "PasswordCheckScreen"),
        "settings":        ("settings_screen",       "SettingsScreen"),
        "add_garden":      ("add_garden",            "AddGardenScreen"),
        "select_garden":   ("select_garden",         "SelectGardenScreen"),
        "export_import":   ("export_import_screen",  "ExportImportScreen"),
        "csv_export":      ("csv_export_screen",     "CsvExportScreen"),
        "photo_gallery":   ("photo_gallery",         "PhotoGalleryScreen"),
    }

    def _create_screen(self, name):
        """Import and instantiate a screen by name."""
        mod_name, cls_name = self._SCREEN_REGISTRY[name]
        import importlib
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        return cls(name=name)

    def _build_remaining_screens(self, already_built, color_a, color_b):
        """Build all screens not yet created."""
        for name in self._SCREEN_REGISTRY:
            if name not in already_built and not self.screen.has_screen(name):
                try:
                    scr = self._create_screen(name)
                    self.screen.add_widget(scr)
                    if hasattr(scr, 'update_shader_colors'):
                        scr.update_shader_colors(color_a, color_b)
                except Exception:
                    LOG.exception("Failed to build screen '%s'", name)

    def go_back(self, instance=None):
        if self.previous_screen:
            self.screen.current = self.previous_screen


if __name__ == "__main__":
    MagicHerbTracker().run()