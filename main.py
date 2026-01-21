import uuid
from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.lang import Builder

from empty_garden import EmptyGardenScreen
from garden_view import GardenViewScreen
from sow_seed import SowSeedScreen
from plant_details import PlantDetailsScreen

# initial window size
Config.set("graphics", "width", "1200")
Config.set("graphics", "height", "800")

# minimum size
Config.set("graphics", "minimum_width", "200")
Config.set("graphics", "minimum_height", "800")

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class MagicHerbTracker(App):
    theme = ObjectProperty(None)
    previous_screen = None

    def build(self):
        self.theme = Factory.Theme()
        self.screen = ScreenManager()
        Window.size = (1200, 800)
        Window.minimum_width = 1200
        Window.minimum_height = 800

        # add screens once
        self.screen.add_widget(EmptyGardenScreen(name="empty_garden"))
        self.screen.add_widget(SowSeedScreen(name="sow_seed"))
        self.screen.add_widget(PlantDetailsScreen(name="plant_details"))
        self.screen.add_widget(GardenViewScreen(name="garden_view"))

        # start on empty garden
        self.screen.current = "empty_garden"
        return self.screen

    def go_back(self, instance):
        # called from any cancel/back button 
        if self.previous_screen:
            self.screen.current = self.previous_screen


if __name__ == "__main__":
    MagicHerbTracker().run()