import datetime
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from helpers import get_difference_days
from storage import load_plant_events
from labels import TitleLabel, FieldLabel, HintLabel
from boxes import WrapperBox, ContentBox, ItemBox, SpacerBox, RedBox, YellowBox, GreenBox, EventBox, SelectableBoxLayout
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import NumTextInput, MedTextInput, LargeTextInput

class EventListView(RecycleView):
    genes = StringProperty("")
    genes_icon = StringProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"  # uses the kv rule above
        self.data = []                    # will fill from GardenViewScreen


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


        content_wrapper = ContentBox(orientation="vertical", size_hint=(1, 1))

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        header = ContentBox(orientation="horizontal", size_hint_y=0.3)
        content_wrapper.add_widget(header)

        title_box = ItemBox(orientation="vertical")
        header.add_widget(title_box)
        spacer_box = SpacerBox(size_hint_y=0.2)
        title_box.add_widget(spacer_box)
        
        name_box = ItemBox(orientation="horizontal", size_hint_y=0.2)
        self.name_label = FieldLabel(text="", valign="middle", halign="left")
        self.name_label.font_size = app.theme.subtitle_size
        self.name_label.color = app.theme.off_white
        name_box.add_widget(self.name_label)
        title_box.add_widget(name_box)

        strain_box = ItemBox(orientation="horizontal", size_hint_y=0.3)
        self.strain_label = FieldLabel(text="", valign="bottom", halign="left")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.off_white

        strain_box.add_widget(self.strain_label)
        title_box.add_widget(strain_box)

        notes_box = ItemBox(orientation="horizontal", size_hint_y=0.15)
        self.notes_label = FieldLabel(text="", valign="middle", halign="left")
        self.notes_label.font_size = app.theme.body_size
        self.notes_label.color = app.theme.off_white

        notes_box.add_widget(self.notes_label)
        title_box.add_widget(notes_box)

        watering_box = ItemBox(orientation="horizontal", size_hint_y=0.15)
        self.last_watering_label = FieldLabel(text="", valign="middle", halign="left")
        self.last_watering_label.font_size = app.theme.body_size
        
        watering_box.add_widget(self.last_watering_label)
        title_box.add_widget(watering_box)

        spacer = SpacerBox(size_hint_x=0.1)
        header.add_widget(spacer)
        days_passed_box = ItemBox(orientation="vertical", size_hint_x=0.3)
        
        days_passed_title = FieldLabel(text="Day:", valign="bottom", halign="right")
        days_passed_title.font_size = app.theme.subtitle_size
        days_passed_box.add_widget(days_passed_title)
        self.days_passed_label = FieldLabel(text="", valign="top", halign="right")
        self.days_passed_label.font_size = app.theme.logo_size_1
        self.days_passed_label.color = app.theme.off_white
        days_passed_box.add_widget(self.days_passed_label)

        header.add_widget(days_passed_box)


        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        info_box = ContentBox(orientation="vertical", size_hint_x=1, size_hint_y=0.8)

        content_wrapper.add_widget(info_box)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        # events scroll 
        scroll_events = ItemBox(orientation="vertical", size_hint_y=0.2, size_hint_x=1)
        self.events_scroll = ScrollView(do_scroll_x=True, do_scroll_y=False,)

        self.events_container = SelectableBoxLayout(orientation="horizontal", size_hint_x=None, size_hint_y=1, padding=5, spacing=0,)
        self.events_container.bind(minimum_width=self.events_container.setter("width"))
        self.events_scroll.add_widget(self.events_container)
        scroll_events.add_widget(self.events_scroll)
        content_wrapper.add_widget(scroll_events)
        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)


        buttons = ItemBox(size_hint_y=0.1)
        go_back_btn = ButtonRed(text="Back")
        go_back_btn.bind(on_press=App.get_running_app().go_back)
        buttons.add_widget(go_back_btn)
        content_wrapper.add_widget(buttons)

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
        app = App.get_running_app()
        plant = self.plant or {}
        self.genes = plant.get("genes", "")
        self.name_label.text = " | ".join([plant.get("name", ""), self.genes])
        
        self.strain_label.text = plant.get("strain", "")
        genes = (self.genes or "").strip().lower()
        if genes == "sativa":
            self.strain_label.color = app.theme.nice_green
        elif genes == "indica":
            self.strain_label.color = app.theme.nice_red
        elif genes == "hybrid":
            self.strain_label.color = app.theme.nice_yellow
        else:
            self.strain_label.color = app.theme.off_white
        self.notes_label.text = plant.get("notes")
        days_passed = get_difference_days(datetime.datetime.now(), plant.get("date_planted", ""))
        self.days_passed_label.text = str(days_passed) if days_passed is not None else "–"
        self._load_and_display_events()

    def _load_and_display_events(self):
        self.events_container.clear_widgets()

        plant = self.plant or {}
        plant_id = plant.get("id")
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

        def _sort_key(event):
            ts_value = event.get("ts") if isinstance(event, dict) else None
            parsed = _parse_ts(ts_value)
            if parsed:
                return (0, parsed)
            return (1, str(ts_value))

        # chronological (oldest -> newest)
        events_sorted = sorted(events, key=_sort_key)

        for event in events_sorted:
            event_type = event.get("type", "")
            feeding = event.get("feeding", "")
            ts = event.get("ts", "")
            days_ago = get_difference_days(datetime.datetime.now(), ts)


            # event box
            box = ContentBox(
                orientation="horizontal",
                size_hint=(None, 1),
                width=200
            )
            info_box = EventBox(orientation='vertical', padding=App.get_running_app().theme.padding_right)
            box.add_widget(info_box)
            
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
            info_box.add_widget(HintLabel(text=str(event_type), font_size="12sp", valign="top"))

            
            
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

    def selected_event_view(self):
        plant = self.plant or {}
        plant_id = plant.get("id")
        if not plant_id:
            return
        events = load_plant_events(str(plant_id))
        
