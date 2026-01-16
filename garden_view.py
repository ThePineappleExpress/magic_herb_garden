import sys
from datetime import date
from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior

from storage import load_plants
from helpers import on_plant_seed, rgba_to_hex

class FieldLabel(Label):
    pass

class TitleBox(BoxLayout):
    pass


class WrapperBox(BoxLayout):
    pass

class ContentBox(BoxLayout):
    pass

class ItemBox(BoxLayout):
    pass

class SpacerBox(BoxLayout):
    pass

class GardenLabel(Label):
    pass

class LogoLabel1(Label):
    pass


class LogoLabel2(Label):
    pass


class LogoLabel3(Label):
    pass
class ListLabel(Label):
    pass
class ListTitleLabel(Label):
    pass
class ListSubLabel(Label):
    pass

class TitleLabel(Label):
    highlight_color = StringProperty("")
    angle = NumericProperty(90)
    text_source = StringProperty("")   # <- used by KV
    hex_color = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        
        # guard in case this is called before theme exists
        if app and hasattr(app, "theme"):
            self.hex_color = rgba_to_hex(app.theme.off_white)
        else:
            self.hex_color = "#ffffff"

class HintLabel(Label):
    pass


class RedBox(ContentBox):
    pass


class YellowBox(ContentBox):
    pass


class GreenBox(ContentBox):
    pass


class ButtonGreen(Button):
    pass


class ButtonRed(Button):
    pass

class NumTextInput(TextInput):
    max_chars = 3
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        if allowed <= 0:
            return
        substring = substring[:allowed]
        super().insert_text(substring, from_undo=from_undo)

class MedTextInput(TextInput):
    max_chars = 32
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        if allowed <= 0:
            return
        substring = substring[:allowed]
        super().insert_text(substring, from_undo=from_undo)

class LargeTextInput(TextInput):
    max_chars = 64
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        if allowed <= 0:
            return
        substring = substring[:allowed]
        super().insert_text(substring, from_undo=from_undo)

class PlantListView(RecycleView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"  # uses the kv rule above
        self.data = []                    # will fill from GardenViewScreen

class GardenViewScreen(Screen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        garden_view = WrapperBox(orientation="horizontal", size_hint_x=1)
        spacer_left = SpacerBox(size_hint_x=0.2)
        stripes_holder = ContentBox(orientation="horizontal")
        stripe_0 = ItemBox(size_hint_x=0.45)
        stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox()
        stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox()
        stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox()
        stripes_holder.add_widget(stripe_3)
        stripe_4 = ItemBox(size_hint_x=0.45)
        stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text = f"My magical [color={TitleLabel().hex_color}]GARDEN[/color]")
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        garden_view.add_widget(spacer_left)

        content_wrapper = ContentBox(orientation="vertical", size_hint=(1, 1))

        title_bar = TitleBox(orientation="horizontal", size_hint_y=0.1)
        spacer = SpacerBox(size_hint_x=0.8)
        title_bar.add_widget(spacer)
        side_menu = ItemBox(orientation='horizontal', size_hint_x=0.2)

        exit_btn = Button(text="Exit\nGarden", size_hint_x=0.5)
        exit_btn.bind(on_press=lambda instance: sys.exit(0))
        side_menu.add_widget(exit_btn)

        title_bar.add_widget(side_menu)

        content_wrapper.add_widget(title_bar)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)
        
        garden_list = ItemBox(orientation="horizontal", size_hint_y=1)

        spacer_box = SpacerBox(size_hint_x=0.02)
        garden_list.add_widget(spacer_box)

        self.plant_list = PlantListView(size_hint_x=1)
        garden_list.add_widget(self.plant_list)

        spacer_box = SpacerBox(size_hint_x=0.02)
        garden_list.add_widget(spacer_box)

        garden_item_preview = RedBox(size_hint_x=0.3)
        garden_list.add_widget(garden_item_preview)


        content_wrapper.add_widget(garden_list)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        garden_footer = ContentBox(orientation="horizontal", size_hint_y=0.1)
        spacer_box = SpacerBox(size_hint_x=0.8)
        garden_footer.add_widget(spacer_box)
        add_plant_btn = Button(text="Add aPlant")
        add_plant_btn.bind(on_press=on_plant_seed)
        garden_footer.add_widget(add_plant_btn)
        view_selected_btn = Button(text="View Selected Plant")
        garden_footer.add_widget(view_selected_btn)
        delete_selected_btn = Button(text="Delete Selected Plant")
        garden_footer.add_widget(delete_selected_btn)

        content_wrapper.add_widget(garden_footer)

        garden_view.add_widget(content_wrapper)

        self.add_widget(garden_view)
        self.refresh_plants()

    def refresh_plants(self):
        plants = load_plants()
        today = date.today()

        data = []
        for p in plants:
            # basic text fields
            name = p.get("name", "")
            strain = p.get("strain", "")
            info = p.get("notes", "")
            genes = p.get("genes", "")  

            # simple “days left” placeholders for now
            # later you can compute from date_planted + watering_profile etc.
            next_watering = "–"
            next_feeding = "–"
            flower_status = "–"
            harvest_status = "–"

            # example: rough days to flower based on estimate and date_planted
            dt_str = p.get("date_planted") or ""
            est_f = p.get("days_to_flower_est")
            est_h = p.get("days_to_harvest_est")
            if dt_str and est_f:
                try:
                    y, m, d = map(int, dt_str.split("-"))
                    planted = date(y, m, d)
                    days_since = (today - planted).days
                    days_left = est_f - days_since
                    if days_left >= 0:
                        flower_status = f"{days_left}"
                    elif days_left <= 0 and est_f  != "Harvested!":
                        flower_status = f"Flowering!"
                    else:
                        flower_status = self.harvest_status
                except Exception:
                    flower_status = f"{est_f}"

            # example: rough days to harvest based on estimate and date_planted
            if dt_str and est_h:
                try:
                    y, m, d = map(int, dt_str.split("-"))
                    planted = date(y, m, d)
                    days_since = (today - planted).days
                    days_left = est_h - days_since
                    if days_left >= 0:
                        harvest_status = f"{days_left}"
                    else:
                        harvest_status = f"Harvested!"
                except Exception:
                    harvest_status = f"{est_h}"
            # for next_watering / next_feeding you can later derive from
            # watering_profile / feeding_profile + days_since

            data.append({
                "genes": genes,
                "name": name,
                "strain": strain,
                "info": info,
                "next_watering": next_watering,
                "next_feeding": next_feeding,
                "flower_status": flower_status,
                "harvest_status": harvest_status,
            })

        self.plant_list.data = data
    

