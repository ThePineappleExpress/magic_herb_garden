import uuid
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
from storage import load_plants
Window.allow_smooth_resize = False

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

    def build(self):
        self.theme = Factory.Theme()
        self.screen = ScreenManager(transition=FadeTransition(duration=0.2))
        Window.size = (1920, 1080)
        Window.minimum_width = 1920
        Window.minimum_height = 1080
        file = load_plants()

        # add screens once
        self.screen.add_widget(EmptyGardenScreen(name="empty_garden"))
        self.screen.add_widget(SowSeedScreen(name="sow_seed"))
        self.screen.add_widget(SetEnvironmentScreen(name="set_environment"))
        self.screen.add_widget(PlantDetailsScreen(name="plant_details"))
        self.screen.add_widget(GardenViewScreen(name="garden_view"))
        self.screen.add_widget(AreYouSure(name="are_you_sure"))
        self.screen.add_widget(AddEventScreen(name="add_event"))
        self.screen.add_widget(TimelineScreen(name="timeline_view"))
        # start on empty garden
        if file == []:
            self.screen.current = "empty_garden"
        else:
            self.screen.current = "garden_view" 
        return self.screen

    def go_back(self, instance=None):
        # called from any cancel/back button 
        if self.previous_screen:
            self.screen.current = self.previous_screen

    
if __name__ == "__main__":
    MagicHerbTracker().run()