import json, os, datetime
from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

from helpers import rgba_to_hex, get_difference_days
from storage import load_plant_events, load_events



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

class LogoLabel1(Label):
    pass


class LogoLabel2(Label):
    pass


class LogoLabel3(Label):
    pass
class HintLabel(Label):
    pass
class EventBox(ItemBox):
    hovered = BooleanProperty(False)
    normal_text_color = ListProperty([1, 1, 1, 1])
    hover_text_color = ListProperty([0, 0, 0, 1])
    normal_bg_color = ListProperty([0, 0, 0, 0])
    hover_bg_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app and hasattr(app, "theme"):
            self.normal_text_color = app.theme.nice_yellow
            self.hover_text_color = app.theme.dark_gray
            self.normal_bg_color = app.theme.black_transparent
            self.hover_bg_color = app.theme.nice_green
        Window.bind(mouse_pos=self._on_mouse_pos)
        self.bind(hovered=self._apply_hover_state)

    def on_parent(self, instance, parent):
        if parent is None:
            Window.unbind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, _window, pos):
        if not self.get_root_window():
            return
        is_hover = self.collide_point(*self.to_widget(*pos))
        if self.hovered != is_hover:
            self.hovered = is_hover

    def add_widget(self, widget, *args, **kwargs):
        super().add_widget(widget, *args, **kwargs)
        self._apply_hover_state()

    def _apply_hover_state(self, *_args):
        color = self.hover_text_color if self.hovered else self.normal_text_color
        for child in self.children:
            if hasattr(child, "color"):
                child.color = color
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

class PlantDetailsScreen(Screen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plant = None
        app = App.get_running_app()

        # build UI 
        detail_view = WrapperBox(orientation="horizontal")
        spacer_left = SpacerBox(size_hint_x=0.2)
        stripes_holder = ContentBox(orientation="horizontal")
        stripe_0 = ItemBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox(); stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox(); stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox(); stripes_holder.add_widget(stripe_3)
        stripe_4 = ItemBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text=f"Just look at this [color={TitleLabel().hex_color}]BEAUTY[/color]")
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        detail_view.add_widget(spacer_left)

        content_wrapper = ContentBox(orientation="horizontal", size_hint=(1, 1))
        content_left = ContentBox(orientation="vertical", size_hint_x=0.1)
        content_wrapper.add_widget(content_left)

        content_right = ContentBox(orientation="vertical")

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_right.add_widget(spacer_box)

        name_box = ItemBox(orientation="vertical", size_hint_x=1, size_hint_y=0.3)
        content_right.add_widget(name_box)

        
        self.name_label = FieldLabel(text="")
        self.name_label.font_size = app.theme.subtitle_size
        name_box.add_widget(self.name_label)

        self.strain_label = FieldLabel(text="")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.off_white
        name_box.add_widget(self.strain_label)

        self.info_label = FieldLabel(text="")
        self.info_label.font_size = app.theme.small_size
        name_box.add_widget(self.info_label)

        self.last_watering_label = FieldLabel(text="")
        self.last_watering_label.font_size = app.theme.small_size
        name_box.add_widget(self.last_watering_label)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_right.add_widget(spacer_box)

        info_box = ContentBox(orientation="vertical", size_hint_x=1, size_hint_y=0.6)

        content_right.add_widget(info_box)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_right.add_widget(spacer_box)

        # events scroll 
        scroll_events = ItemBox(orientation="vertical", size_hint_y=0.2, size_hint_x=1)
        self.events_scroll = ScrollView(do_scroll_x=True, do_scroll_y=False,)

        self.events_container = BoxLayout(orientation="horizontal", size_hint_x=None, size_hint_y=1, padding=5, spacing=0,)
        self.events_container.bind(minimum_width=self.events_container.setter("width"))
        self.events_scroll.add_widget(self.events_container)
        scroll_events.add_widget(self.events_scroll)
        content_right.add_widget(scroll_events)
        spacer_box = SpacerBox(size_hint_y=0.02)
        content_right.add_widget(spacer_box)



        content_wrapper.add_widget(content_right)

        buttons = ItemBox(size_hint_y=0.1)
        go_back_btn = ButtonRed(text="Back")
        go_back_btn.bind(on_press=App.get_running_app().go_back)
        buttons.add_widget(go_back_btn)
        content_right.add_widget(buttons)

        detail_view.add_widget(content_wrapper)
        spacer_right = SpacerBox(size_hint_x=0.1)
        detail_view.add_widget(spacer_right)
        self.add_widget(detail_view)

        # load and show events
        self._load_and_display_events()

    def set_plant(self, plant: dict):
        self.plant = plant or {}
        self._update_ui()

    def _update_ui(self):
        plant = self.plant or {}
        self.name_label.text = plant.get("name", "")
        self.strain_label.text = plant.get("strain", "")
        self.info_label.text = plant.get("notes", "")
        self._load_and_display_events()

    def _load_and_display_events(self):
        self.events_container.clear_widgets()

        plant = self.plant or {}
        plant_id = plant.get("id") or plant.get("plant_id")
        if not plant_id:
            return

        data = load_plant_events(str(plant_id))
        if not data:
            return
        events = data.get("events", [])
        if not events:
            return

        def _parse_ts(value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return datetime.datetime.fromtimestamp(value)
            if isinstance(value, str):
                return datetime.datetime.fromisoformat(value)
            return None

        def _sort_key(evt):
            ts_value = evt.get("ts") if isinstance(evt, dict) else None
            parsed = _parse_ts(ts_value)
            if parsed:
                return (0, parsed)
            return (1, str(ts_value))

        # chronological (oldest -> newest)
        events_sorted = sorted(events, key=_sort_key)

        for evt in events_sorted:
            evt_type = evt.get("type", "")
            feeding = evt.get("feeding", "")
            ts = evt.get("ts", "")
            days_ago = get_difference_days(datetime.datetime.now(), ts)


            # event box
            box = ContentBox(
                orientation="horizontal",
                size_hint=(None, 1),
                width=200
            )
            info_box = EventBox(orientation='vertical', padding=App.get_running_app().theme.padding_right)
            box.add_widget(info_box)
            # you can format ts to date-only if you like
            if days_ago == 0:
                info_box.add_widget(HintLabel(text="Today", font_size="12sp", valign="bottom"))
            elif days_ago == 1:
                info_box.add_widget(HintLabel(text="Yesterday", font_size="12sp", valign="bottom"))
            elif days_ago > 1 and days_ago < 7:
                info_box.add_widget(HintLabel(text=f"{days_ago} days ago", font_size="12sp", valign="bottom"))
            elif days_ago >= 7 and days_ago < 30:
                weeks = days_ago // 7
                if days_ago < 14:
                    s = ""
                else:
                    s = "s"
                info_box.add_widget(HintLabel(text=f"{weeks} week{s} ago", font_size="12sp", valign="bottom"))
            elif days_ago >= 30 and days_ago < 365:
                months = days_ago // 30
                if days_ago < 60:
                    s = ""
                else:
                    s = "s"
                info_box.add_widget(HintLabel(text=f"{months} month{s} ago", font_size="12sp", valign="bottom"))
            elif days_ago >= 365:
                years = days_ago // 365
                if days_ago < 730:
                    s = ""
                else:
                    s = "s"
                info_box.add_widget(HintLabel(text=f"{years} year{s} ago", font_size="12sp", valign="bottom"))
            else:
                info_box.add_widget(SpacerBox())
            
            
            if feeding != None:
                info_box.add_widget(HintLabel(text=str("feeding"), font_size="12sp", valign="middle"))
            else:
                info_box.add_widget(SpacerBox())
            info_box.add_widget(HintLabel(text=str(evt_type), font_size="12sp", valign="top"))

            
            
            color_bar = ItemBox(orientation="vertical", size_hint_x=0.005)
            color_bar.add_widget(RedBox())
            color_bar.add_widget(YellowBox())
            color_bar.add_widget(GreenBox())
            box.add_widget(color_bar)
            self.events_container.add_widget(box)

        # last event summary 
        last = events_sorted[-1]
        if last.get("type") == "watering":
            vol = last.get("volume_l")
            ph = last.get("ph")
            ppm = last.get("ppm")
            ts = last.get("ts")
            self.last_watering_label.text = f"Last watering: {vol} L, pH {ph}, {ppm} ppm @ {ts}"
        else:
            self.last_watering_label.text = f"Last event: {last.get('type')} @ {last.get('ts')}"

        Clock.schedule_once(lambda *_: setattr(self.events_scroll, "scroll_x", 1), 0)
