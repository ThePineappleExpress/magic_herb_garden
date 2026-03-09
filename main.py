import logging

from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from empty_garden import EmptyGardenScreen
from garden_view import GardenViewScreen
from sow_seed import SowSeedScreen
from set_environment import SetEnvironmentScreen
from plant_details import PlantDetailsScreen
from are_you_sure import AreYouSure
from add_event import AddEventScreen
from timeline_view import TimelineScreen
from password_check import PasswordCheckScreen
from settings_screen import SettingsScreen
from add_garden import AddGardenScreen
from select_garden import SelectGardenScreen
from export_import_screen import ExportImportScreen
from csv_export_screen import CsvExportScreen
from bin.themes import load_theme, apply_theme, get_default_theme, get_shader_colors
import lang
import storage

Window.allow_smooth_resize = False

LOG = logging.getLogger(__name__)

# initial window size
Config.set("graphics", "width", "1280")
Config.set("graphics", "height", "720")

# minimum size
Config.set("graphics", "minimum_width", "1280")
Config.set("graphics", "minimum_height", "720")

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class MagicHerbTracker(App):
    theme = ObjectProperty(None)
    previous_screen = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pending_plant_data = {}
        self.current_garden_id = None
        self.post_garden_select_screen = "garden_view"
        self.post_unlock_screen = None

    def build(self):
        self.theme = Factory.Theme()
        self.screen = ScreenManager(transition=FadeTransition(duration=0.2))
        Window.size = (1920, 1080)
        Window.minimum_width = 1920
        Window.minimum_height = 1080

        # Register all screens
        self.screen.add_widget(EmptyGardenScreen(name="empty_garden"))
        self.screen.add_widget(SowSeedScreen(name="sow_seed"))
        self.screen.add_widget(SetEnvironmentScreen(name="set_environment"))
        self.screen.add_widget(PlantDetailsScreen(name="plant_details"))
        self.screen.add_widget(GardenViewScreen(name="garden_view"))
        self.screen.add_widget(AreYouSure(name="are_you_sure"))
        self.screen.add_widget(AddEventScreen(name="add_event"))
        self.screen.add_widget(TimelineScreen(name="timeline_view"))
        self.screen.add_widget(PasswordCheckScreen(name="password_check"))
        self.screen.add_widget(SettingsScreen(name="settings"))
        self.screen.add_widget(AddGardenScreen(name="add_garden"))
        self.screen.add_widget(SelectGardenScreen(name="select_garden"))
        self.screen.add_widget(ExportImportScreen(name="export_import"))
        self.screen.add_widget(CsvExportScreen(name="csv_export"))

        # Apply saved theme
        settings = storage.load_settings()
        theme_name = settings.get("theme", get_default_theme())
        theme_data = load_theme(theme_name)
        apply_theme(self.theme, theme_data)

        # Push shader colors to all screens
        shader_name = settings.get("shader")
        color_a, color_b = get_shader_colors(theme_data, shader_name)
        for scr in self.screen.screens:
            if hasattr(scr, 'update_shader_colors'):
                scr.update_shader_colors(color_a, color_b)

        # Bootstrap: password → garden selection → garden view
        has_password = bool(settings.get("password"))
        gardens = storage.load_gardens()

        if has_password:
            # Determine where to go after unlock
            if len(gardens) == 1:
                self.current_garden_id = gardens[0].get("id")
                self.post_unlock_screen = "garden_view"
            elif len(gardens) > 1:
                self.post_unlock_screen = "select_garden"
            else:
                self.post_unlock_screen = "add_garden"
            self.screen.current = "password_check"
        elif len(gardens) == 1:
            self.current_garden_id = gardens[0].get("id")
            self.screen.current = "garden_view"
        elif len(gardens) > 1:
            self.screen.current = "select_garden"
        else:
            self.screen.current = "add_garden"

        return self.screen

    def go_back(self, instance=None):
        if self.previous_screen:
            self.screen.current = self.previous_screen


if __name__ == "__main__":
    MagicHerbTracker().run()