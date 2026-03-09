import datetime
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from helpers import get_difference_days, go_to_add_event, go_to_garden, go_to_timeline
from storage import load_plant_events
from constants import (
    EVENT_WATERING, EVENT_FEEDING, EVENT_PLANTING, EVENT_HARVEST,
)
from labels import TitleLabel, FieldLabel, HintLabel, NutrientLabel, ListTitleLabel, LogoLabel2
from boxes import ItemBox, WrapperBox, ContentBox, SpacerBox, RedBox, YellowBox, GreenBox, EventBox, SelectableBoxLayout, SelectableEventBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow, ButtonTransparent
from text_inputs import NumTextInput, MedTextInput, LargeTextInput
from screens import BaseScreen
import lang

class HorizontalScrollView(ScrollView):
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if 'button' in touch.profile:
                # Find the container with event boxes
                container = self.children[0] if self.children else None
                if container:
                    num_events = len(container.children)
                    # Estimate how many events fit in the visible area
                    if num_events > 0 and container.children[0].width > 0:
                        visible_events = int(self.width // container.children[0].width)
                    else:
                        visible_events = 1
                    # Calculate step so you can scroll through all events
                    step = 0.1 / max(1, num_events - visible_events + 1)
                else:
                    step = 0.001  # fallback

                if touch.button == 'scrolldown':
                    self.scroll_x = min(self.scroll_x + step, 1)
                    return True
                elif touch.button == 'scrollup':
                    self.scroll_x = max(self.scroll_x - step, 0)
                    return True
        return super().on_touch_down(touch)

class PlantDetailsScreen(BaseScreen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plant = None
        self._selected_event_item = None
        app = App.get_running_app()

        # build UI 
        plant_details_screen = WrapperBox(orientation="horizontal")
        spacer_left = SpacerBox(size_hint_x=0.2)
        stripes_holder = WrapperBox(orientation="horizontal")
        stripe_0 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox(); stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox(); stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox(); stripes_holder.add_widget(stripe_3)
        stripe_4 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text=lang.SCREEN_TITLE_DETAILS.format(color=TitleLabel().hex_color))
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        plant_details_screen.add_widget(spacer_left)

        content_wrapper = WrapperBox(orientation="vertical", size_hint=(1, 1))

        spacer_box = SpacerBox(size_hint_y=0.1)
        content_wrapper.add_widget(spacer_box)

        header = WrapperBox(orientation="horizontal", size_hint_y=0.3)
        content_wrapper.add_widget(header)

        title_box = ContentBox(orientation="vertical")
        header.add_widget(title_box)
        spacer_box = SpacerBox(size_hint_y=0.2)
        title_box.add_widget(spacer_box)
        
        name_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        self.name_label = FieldLabel(text="", valign="middle", halign="left")
        self.name_label.font_size = app.theme.subtitle_size
        self.name_label.color = app.theme.color_field_value
        name_box.add_widget(self.name_label)
        title_box.add_widget(name_box)

        strain_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        self.strain_label = FieldLabel(text="", valign="middle", halign="left")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.color_field_value

        strain_box.add_widget(self.strain_label)
        title_box.add_widget(strain_box)

        notes_box = ContentBox(orientation="horizontal", size_hint_y=0.15)
        self.notes_label = FieldLabel(text="", valign="middle", halign="left")
        self.notes_label.font_size = app.theme.body_size
        self.notes_label.color = app.theme.color_field_value

        notes_box.add_widget(self.notes_label)
        title_box.add_widget(notes_box)

        water_data_box = ContentBox(orientation="horizontal", size_hint_y=0.15)
        self.last_water_label = FieldLabel(text="", valign="middle", halign="left")
        self.last_water_label.font_size = app.theme.body_size
        
        water_data_box.add_widget(self.last_water_label)
        title_box.add_widget(water_data_box)

        spacer = SpacerBox(size_hint_x=0.1)
        header.add_widget(spacer)
        days_passed_box = ContentBox(orientation="vertical", size_hint_x=0.2)
        header.add_widget(days_passed_box)
        
        spacer_box = SpacerBox(size_hint_y=0.3)
        days_passed_box.add_widget(spacer_box)

        days_passed_title_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        days_passed_box.add_widget(days_passed_title_box)
        days_passed_title = FieldLabel(text=lang.DAY_LABEL, valign="middle", halign="right")
        days_passed_title.font_size = app.theme.subtitle_size        
        days_passed_title_box.add_widget(days_passed_title)

        days_passed_value_box = ContentBox(orientation="horizontal", size_hint_y=0.5)
        days_passed_box.add_widget(days_passed_value_box)
        self.days_passed_value = FieldLabel(text="", valign="middle", halign="right")
        self.days_passed_value.font_size = app.theme.logo_size_1
        self.days_passed_value.color = app.theme.color_field_value
        days_passed_value_box.add_widget(self.days_passed_value)

        days_stage_box = ContentBox(orientation="vertical", size_hint_y=0.1)
        days_passed_box.add_widget(days_stage_box)
        self.days_stage_value = FieldLabel(text="", valign="middle", halign="right")
        self.days_stage_value.font_size = app.theme.body_size
        self.days_stage_value.color = app.theme.color_field_value
        days_stage_box.add_widget(self.days_stage_value)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        self.info_box = WrapperBox(orientation="vertical", size_hint_x=1, size_hint_y=0.8)

        content_wrapper.add_widget(self.info_box)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        # events scroll 
        scroll_events = ContentBox(orientation="horizontal", size_hint_y=0.3)
        view_timeline_button = ButtonTransparent(text=lang.VIEW_TIMELINE, size_hint_x=0.2)
        view_timeline_button.bind(on_release=lambda instance: go_to_timeline(instance, self.plant))
        scroll_events.add_widget(view_timeline_button)
        self.events_scroll = HorizontalScrollView(do_scroll_x=True, do_scroll_y=False, scroll_distance=0.1, scroll_timeout=250,)

        self.events_container = WrapperBox(orientation="horizontal", size_hint_x=None, size_hint_y=1, padding=5, spacing=0,)
        self.events_container.bind(minimum_width=self.events_container.setter("width"))
        self.events_scroll.add_widget(self.events_container)
        scroll_events.add_widget(self.events_scroll)
        add_event_box = WrapperBox(orientation="horizontal", size_hint_x=0.1)
        scroll_events.add_widget(add_event_box)
        add_event_button = ButtonYellow(text=lang.BUTTON_PLUS)
        add_event_button.font_size = app.theme.logo_size_1
        add_event_button.font_name = app.theme.font_logo_1
        def safe_go_to_add_event(instance):
            plant = self.plant or {}
            # Patch: ensure plant_id is present for AddEventScreen
            if 'plant_id' not in plant and 'id' in plant:
                plant = dict(plant)
                plant['plant_id'] = plant['id']
            go_to_add_event(self, plant)
            # If we have a last-event-today, pass it to AddEventScreen for editing
            if self._last_event_today:
                add_event_screen = app.screen.get_screen('add_event')
                add_event_screen._selected_event_data = self._last_event_today
        add_event_button.bind(on_release=safe_go_to_add_event)
        self.add_event_button = add_event_button
        self._last_event_today = None
        add_event_box.add_widget(add_event_button)
        content_wrapper.add_widget(scroll_events)
        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        buttons = ContentBox(size_hint_y=0.1)
        go_back_btn = ButtonRed(text=lang.BACK)
        go_back_btn.bind(on_release=go_to_garden)
        buttons.add_widget(go_back_btn)
        content_wrapper.add_widget(buttons)

        plant_details_screen.add_widget(content_wrapper)
        spacer_right = SpacerBox(size_hint_x=0.1)
        plant_details_screen.add_widget(spacer_right)
        self.add_widget(plant_details_screen)

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
            self.strain_label.color = app.theme.color_strain_sativa
        elif genes == "indica":
            self.strain_label.color = app.theme.color_strain_indica
        elif genes == "hybrid":
            self.strain_label.color = app.theme.color_strain_hybrid
        else:
            self.strain_label.color = app.theme.color_strain_unknown
        self.notes_label.text = plant.get("notes") or ""
        days_passed = get_difference_days(datetime.datetime.now(), plant.get("date_planted", ""))
        self.days_passed_value.text = str(days_passed) if days_passed is not None else "–"
        self._load_and_display_events()

    def _select_event_item(self, item, event):
        if self._selected_event_item and self._selected_event_item != item:
            self._selected_event_item.selected = False
        item.selected = True
        self._selected_event_item = item
        self._selected_event_data = event 
        self.selected_event_view()

    def _load_and_display_events(self):
        self.events_container.clear_widgets()
        self._selected_event_item = None

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

        event_boxes = []

        for event in events_sorted:
            event_type = event.get("type", "")
            feeding = event.get("feeding", "")
            ts = event.get("ts", "")
            days_ago = get_difference_days(datetime.datetime.now(), ts)

            # selectable event item
            box = SelectableEventBox(orientation="horizontal", size_hint=(None, 1), width=200)
            box.bind(on_release=lambda _btn, _event=event, _item=box: self._select_event_item(_item, _event))

            event_boxes.append((box, event))  # Track box and event

            info_box = EventBox(orientation='vertical', padding=App.get_running_app().theme.padding_right)
            box.add_widget(info_box)
            
            if days_ago == 0:
                info_box.add_widget(HintLabel(text=lang.TODAY, font_size="12sp", valign="bottom"))
            elif days_ago == 1:
                info_box.add_widget(HintLabel(text=lang.YESTERDAY, font_size="12sp", valign="bottom"))
            elif days_ago > 1 and days_ago < 7:
                info_box.add_widget(HintLabel(text=lang.DAYS_AGO.format(n=days_ago), font_size="12sp", valign="bottom"))
            elif days_ago >= 7 and days_ago < 30:
                weeks = days_ago // 7
                if days_ago < 14:
                    info_box.add_widget(HintLabel(text=lang.WEEK_AGO_ONE.format(n=weeks), font_size="12sp", valign="bottom"))
                else:
                    info_box.add_widget(HintLabel(text=lang.WEEK_AGO_PLURAL.format(n=weeks), font_size="12sp", valign="bottom"))
            elif days_ago >= 30 and days_ago < 365:
                months = days_ago // 30
                if days_ago < 60:
                    info_box.add_widget(HintLabel(text=lang.MONTH_AGO_ONE.format(n=months), font_size="12sp", valign="bottom"))
                else:
                    info_box.add_widget(HintLabel(text=lang.MONTH_AGO_PLURAL.format(n=months), font_size="12sp", valign="bottom"))
            elif days_ago >= 365:
                years = days_ago // 365
                if days_ago < 730:
                    info_box.add_widget(HintLabel(text=lang.YEAR_AGO_ONE.format(n=years), font_size="12sp", valign="bottom"))
                else:
                    info_box.add_widget(HintLabel(text=lang.YEAR_AGO_PLURAL.format(n=years), font_size="12sp", valign="bottom"))
            else:
                info_box.add_widget(SpacerBox())
            
            status_box = ContentBox(orientation="horizontal")
            info_box.add_widget(status_box)
            
            status_text = HintLabel(text=f"{self.get_health_indicator(event.get('plant', {}))}")
            status_box.add_widget(status_text)
            
            info_box.add_widget(SpacerBox())
            info_box.add_widget(HintLabel(text=str(event_type), font_size="12sp", valign="top"))
            
            color_bar = ContentBox(orientation="vertical", size_hint_x=0.005)
            color_bar.add_widget(RedBox())
            color_bar.add_widget(YellowBox())
            color_bar.add_widget(GreenBox())
            box.add_widget(color_bar)
            self.events_container.add_widget(box)

        # last event summary 
        last = events_sorted[-1]
        if last.get("type") == EVENT_WATERING:
            vol = last.get("volume_l")
            ph = last.get("ph")
            ppm = last.get("ppm")
            ts = last.get("ts")
            self.last_water_label.text = f"Last water: {vol} L, pH {ph}, {ppm} ppm @ {ts}"
        else:
            self.last_water_label.text = f"Last event: {last.get('type')} @ {last.get('ts')}"

        Clock.schedule_once(lambda *_: setattr(self.events_scroll, "scroll_x", 1), 0)
        if event_boxes:
            last_box, last_event = event_boxes[-1]
            Clock.schedule_once(lambda *_: self._select_event_item(last_box, last_event), 0)

        # Edit-last-event: if last event was today, change + to "Edit"
        app = App.get_running_app()
        last_ts = last.get("ts", "")
        last_date_str = str(last_ts)[:10] if last_ts else ""
        today_str = datetime.date.today().isoformat()
        if last_date_str == today_str and last.get("type") != EVENT_HARVEST:
            self._last_event_today = last
            if hasattr(self, 'add_event_button'):
                self.add_event_button.text = lang.BUTTON_EDIT if hasattr(lang, 'BUTTON_EDIT') else "Edit"
                self.add_event_button.font_size = app.theme.body_size
                self.add_event_button.font_name = app.theme.font_body
        else:
            self._last_event_today = None
            if hasattr(self, 'add_event_button'):
                self.add_event_button.text = lang.BUTTON_PLUS
                self.add_event_button.font_size = app.theme.logo_size_1
                self.add_event_button.font_name = app.theme.font_logo_1

        # Disable add-event if plant has been harvested
        has_harvest = any(
            isinstance(e, dict) and e.get("type") == EVENT_HARVEST
            for e in events
        )
        if hasattr(self, 'add_event_button'):
            self.add_event_button.disabled = has_harvest

    def get_nutrient(self, plant_dict, key):
        deficiencies = plant_dict.get("deficiencies", {})
        excess = plant_dict.get("excess", {})
        if deficiencies.get(key):
            return "deficient"
        elif excess.get(key):
            return "excess"
        else:
            return False

    def get_health_indicator(self, plant=None):
        indicators = []
        plant = plant or self.plant or {}
        coloration = plant.get("leaf_color", "normal")
        morphology = plant.get("leaf_morphology", "normal")
        for nutrient in ['n','p','k','ca','mg','s','fe','mn','zn','cu','b','mo']:
            status = self.get_nutrient(plant, nutrient)
            if status == "deficient":
                indicators.append(f"{nutrient.upper()}↓")
            elif status == "excess":
                indicators.append(f"{nutrient.upper()}↑")
        if len(indicators) == 0 and coloration == "normal" and morphology == "normal":
            return "Healthy"
        elif len(indicators) <= 3 and coloration == "normal" and morphology == "normal":
            return "Minor issues"
        elif len(indicators) > 3 and (coloration != "normal" or morphology == "normal"):
            return "Moderate issues"
        elif len(indicators) > 3 and coloration != "normal" and morphology != "normal":
            return "Severe issues"
        else:
            return "Minor issues"

    def selected_event_view(self):
        self.info_box.clear_widgets()
        app = App.get_running_app()
        plant = self.plant or {}
        event = getattr(self, '_selected_event_data', None) 
        if not event:
            return
        event_date = event.get("ts", "")
        formatter = []
        split_date = event_date.split("-")
        self.days_passed = get_difference_days(event.get("ts", ""), plant.get("date_planted", ""))
        self.days_passed_value.text = str(self.days_passed) if self.days_passed is not None else "–"
        for i in split_date[::-1]:
            formatter.append(i)
        formatted_date = " ".join(formatter)
        event_type = event.get("type", "")
        notes = event.get("notes", "")
        water_volume = event.get("volume_l", "")
        water_temperature = event.get("water_temp_c", "")
        ph = event.get("ph", "")
        ppm = event.get("ppm", "")

        if event.get("type") == EVENT_FEEDING:
            feeding = event.get("feeding") or {}
            grow_mix = feeding.get("grow_mix", 0)
            root_mix = feeding.get("root_mix", 0)
            bloom_mix = feeding.get("bloom_mix", 0)
            bloom_boost = feeding.get("bloom_boost", 0)
            soil_boost = feeding.get("soil_boost", 0)
            vit_boost = feeding.get("vit_boost", 0)
            CalMag = feeding.get("CalMag", 0)
            myco_trico = bool(feeding.get("myco_trico", False))

        plant_obs = event.get("plant") or {}
        stage = plant_obs.get("stage", "")
        plant_height = plant_obs.get("plant_height", "")
        number_of_nodes = plant_obs.get("num_nodes", "")
        node_spacing = plant_obs.get("node_spacing", "")
        main_stems = plant_obs.get("main_stem_number", "")
        coloration = plant_obs.get("leaf_color", "")
        morphology = plant_obs.get("leaf_morphology", "")

        days_stage = stage
        self.days_stage_value.text = f"{days_stage}" if days_stage is not None else "–"

        environment = event.get("environment") or {}
        soil_moisture = environment.get("soil_moisture", "")
        air_temperature = environment.get("air_temp_c", "")
        soil_ph = environment.get("soil_ph", "")
        humidity = environment.get("rh_percent", "")
        vpd = environment.get("vpd_kpa", "")
        light_schedule = environment.get("light_schedule", "")
        ppfd = environment.get("ppfd", "")
            
        health = self.get_health_indicator(plant_obs)

        event_details = WrapperBox(orientation="vertical")

        event_title_row = WrapperBox(orientation="horizontal", size_hint_y=0.4)
        event_details.add_widget(event_title_row)

        date_and_type_box = WrapperBox(orientation="vertical", size_hint_x=0.3)
        event_title_row.add_widget(date_and_type_box)

        event_date_label_box =  ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(event_date_label_box)
        event_date_value = FieldLabel(text=f"{formatted_date}", valign="middle", halign="left")
        event_date_value.color = app.theme.color_field_value
        event_date_value.font_size = app.theme.title_size
        event_date_label_box.add_widget(event_date_value)

        event_type_label_box = ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(event_type_label_box)
        event_type_label = FieldLabel(text=f"{event_type}", valign="middle", halign="left")
        if event_type == EVENT_WATERING:
            event_type_label.color = app.theme.color_event_watering
        elif event_type == EVENT_FEEDING:
            event_type_label.color = app.theme.color_event_feeding
        else:
            event_type_label.color = app.theme.color_event_default
        event_type_label.font_size = app.theme.subtitle_size
        event_type_label_box.add_widget(event_type_label)

        health_indicator_box = ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(health_indicator_box)
        health_indicator_label = FieldLabel(text=f"{health}", valign="middle", halign="left")
        if health == "Healthy":
            health_indicator_label.color = app.theme.color_health_healthy
        elif health == "Minor issues":
            health_indicator_label.color = app.theme.color_health_minor
        elif health == "Moderate issues":
            health_indicator_label.color = app.theme.color_health_moderate
        elif health == "Severe issues":
            health_indicator_label.color = app.theme.color_health_severe  
        health_indicator_label.font_size = app.theme.body_size
        health_indicator_box.add_widget(health_indicator_label)
        
        # Refactored: Generate event info fields in a loop
        plant_and_environment_box = WrapperBox(orientation="vertical", size_hint_x=0.7)
        event_title_row.add_widget(plant_and_environment_box)

        # Define event info fields: (title, value, source_dict, key, special)
        event_info_fields = [
            ("Height", plant, "plant_height", False),
            ("Nodes", plant, "num_nodes", False),
            ("Spacing", plant, "node_spacing", False),
            ("Main Stems", plant, "main_stem_number", False),
            ("Color", plant, "leaf_color", False),
            ("Morphology", plant, "leaf_morphology", False),
            ("Air Temp", environment, "air_temp_c", False),
            ("Humidity", environment, "rh_percent", False),
            ("VPD", environment, "vpd_kpa", False),
            ("Soil pH", environment, "soil_ph", False),
            ("Soil", environment, "soil_moisture", False),
            ("PPFD", environment, "ppfd", False),
            ("Light", environment, "light_schedule", False),
        ]

        # Split into two rows: plant info and environment info
        plant_row = WrapperBox(orientation="horizontal")
        env_row = WrapperBox(orientation="horizontal")
        plant_and_environment_box.add_widget(plant_row)
        plant_and_environment_box.add_widget(env_row)

        # Helper to get value and format
        def get_event_value(source, key, special):
            val = source.get(key, None)
            if special:
                return "Yes" if val else "No"
            if val is None:
                return "–"
            if isinstance(val, list):
                return "/".join(map(str, val))
            return str(val)

        # Plant + env
        for i, (title, source, key, special) in enumerate(event_info_fields):
            box = WrapperBox(orientation="vertical")
            # Title
            title_box = ContentBox(orientation="horizontal")
            label = FieldLabel(text=title, valign="bottom", halign="left")
            label.color = app.theme.color_field_label
            label.font_size = app.theme.small_size
            title_box.add_widget(label)
            box.add_widget(title_box)
            # Value
            value_box = ContentBox(orientation="horizontal")
            value = get_event_value(source, key, special)
            value_label = FieldLabel(text=value, valign="top", halign="left")
            value_label.font_size = app.theme.subtitle_size
            if special:
                value_label.color = app.theme.color_field_label if value == "Yes" else app.theme.color_label_body
            else:
                value_label.color = app.theme.color_field_value
            value_box.add_widget(value_label)
            box.add_widget(value_box)
            # Add to row
            if i < 6:
                plant_row.add_widget(box)
            elif i < 12:
                env_row.add_widget(box)
            else:
                env_row.add_widget(box)

        main_data_column = WrapperBox(orientation="horizontal")
        event_details.add_widget(main_data_column)

        water_and_food_box = WrapperBox(orientation="vertical", size_hint_x=0.4)
        main_data_column.add_widget(water_and_food_box)

        # Watering/Feeding fields (no units, looped)
        if event_type in (EVENT_WATERING, EVENT_FEEDING):
            water_row = WrapperBox(orientation="horizontal", size_hint_y=0.2)
            water_and_food_box.add_widget(water_row)
            water_fields = [
                ("Volume", water_volume),
                ("Temp", water_temperature),
                ("pH", ph),
                ("PPM", ppm),
            ]
            for title, value in water_fields:
                box = WrapperBox(orientation="vertical")
                title_box = ContentBox(orientation="horizontal")
                label = FieldLabel(text=title, valign="bottom", halign="left")
                label.color = app.theme.color_water_label
                label.font_size = app.theme.small_size
                title_box.add_widget(label)
                box.add_widget(title_box)
                value_box = ContentBox(orientation="horizontal")
                value_label = FieldLabel(text=str(value) if value not in (None, "") else "–", valign="top", halign="left")
                value_label.font_size = app.theme.subtitle_size
                value_label.color = app.theme.color_field_value
                value_box.add_widget(value_label)
                box.add_widget(value_box)
                water_row.add_widget(box)
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)

        # Feeding fields (looped, special logic for stage)
        if event_type == EVENT_FEEDING:
            # Row 1: Veg/Root/Soil/Vit
            feeding_row_1 = WrapperBox(orientation="horizontal", size_hint_y=0.2)
            water_and_food_box.add_widget(feeding_row_1)
            feeding_fields_1 = []
            if stage == "vegetative":
                feeding_fields_1.append(("Veg", grow_mix))
            else:
                feeding_fields_1.append(("Veg", None))
            feeding_fields_1 += [
                ("Root", root_mix),
                ("Soil", soil_boost),
                ("Vit", vit_boost),
            ]
            for title, value in feeding_fields_1:
                box = WrapperBox(orientation="vertical")
                title_box = ContentBox(orientation="horizontal")
                label = FieldLabel(text=title, valign="bottom", halign="left")
                label.color = app.theme.color_feed_label
                label.font_size = app.theme.small_size
                title_box.add_widget(label)
                box.add_widget(title_box)
                value_box = ContentBox(orientation="horizontal")
                value_label = FieldLabel(text=str(value) if value not in (None, "") else "–", valign="top", halign="left")
                value_label.font_size = app.theme.subtitle_size
                value_label.color = app.theme.color_field_value
                value_box.add_widget(value_label)
                box.add_widget(value_box)
                feeding_row_1.add_widget(box)

            # Row 2: Flower/Tops/CalMag/Fungi
            feeding_row_2 = WrapperBox(orientation="horizontal", size_hint_y=0.2)
            water_and_food_box.add_widget(feeding_row_2)
            feeding_fields_2 = []
            if stage == "flowering":
                feeding_fields_2.append(("Flower", bloom_mix))
                feeding_fields_2.append(("Tops", bloom_boost))
            else:
                feeding_fields_2.append(("Flower", None))
                feeding_fields_2.append(("Tops", None))
            feeding_fields_2.append(("CalMag", CalMag))
            # Fungi special logic
            fungi_val = "Yes" if myco_trico else "No"
            feeding_fields_2.append(("Fungi", fungi_val))
            for i, (title, value) in enumerate(feeding_fields_2):
                box = WrapperBox(orientation="vertical")
                title_box = ContentBox(orientation="horizontal")
                label = FieldLabel(text=title, valign="bottom", halign="left")
                label.color = app.theme.color_feed_label
                label.font_size = app.theme.small_size
                title_box.add_widget(label)
                box.add_widget(title_box)
                value_box = ContentBox(orientation="horizontal")
                value_label = FieldLabel(text=str(value) if value not in (None, "") else "–", valign="top", halign="left")
                value_label.font_size = app.theme.subtitle_size
                if title == "Fungi":
                    value_label.color = app.theme.color_field_label if value == "Yes" else app.theme.color_label_body
                else:
                    value_label.color = app.theme.color_field_value
                value_box.add_widget(value_label)
                box.add_widget(value_box)
                feeding_row_2.add_widget(box)
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)

        right_column_box = WrapperBox(orientation="vertical", size_hint_x=0.3)
        main_data_column.add_widget(right_column_box)

        nutrients_box = WrapperBox(orientation="vertical", size_hint_y = 0.4)
        right_column_box.add_widget(nutrients_box)

        nutrients_title_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        nutrients_box.add_widget(nutrients_title_box)

        nutrients_title = FieldLabel(text=lang.NUTRIENTS, valign="bottom", halign="left")
        nutrients_title.color = app.theme.color_field_label
        nutrients_title.font_size = app.theme.body_size
        nutrients_title_box.add_widget(nutrients_title)

        nutrients_data_box = ContentBox(orientation="horizontal", size_hint_y=0.8, spacing=0)
        nutrients_box.add_widget(nutrients_data_box)
        

        for nutrient in ["n","p","k","ca","mg","s","fe","mn","zn","cu","b","mo"]:
            box = GreenBox(orientation="vertical", spacing=0, padding=0, size_hint=(1, 1))
            nutrients_data_box.add_widget(box)
            for text in ["+", nutrient.capitalize(), "-"]:
                if text == "+":
                    if self.get_nutrient(plant_obs, nutrient) == "excess":
                        sub_box = YellowBox(orientation="vertical")
                    else:
                        sub_box = GreenBox(orientation="vertical")        
                elif text == "-":
                    if self.get_nutrient(plant_obs, nutrient) == "deficient":
                        sub_box = YellowBox(orientation="vertical")
                    else:
                        sub_box = GreenBox(orientation="vertical")        
                else:
                    sub_box = GreenBox(orientation="vertical", size_hint_x=1)
                    label = NutrientLabel(text=nutrient.capitalize(), valign="middle", halign="center", size_hint_x=1)
                    label.font_name = app.theme.font_logo_2
                    label.color = app.theme.color_button_bg
                    label.font_size = app.theme.subtitle_size
                    label.text_size = label.size
                    label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
                    sub_box.add_widget(label)
                box.add_widget(sub_box)

        notes_box = WrapperBox(orientation="vertical", size_hint_y = 0.6)
        right_column_box.add_widget(notes_box)

        notes_title_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        notes_box.add_widget(notes_title_box)
        notes_title = FieldLabel(text=lang.LABEL_NOTES, valign="bottom", halign="left")
        notes_title.color = app.theme.color_field_label
        notes_title.font_size = app.theme.subtitle_size
        notes_title_box.add_widget(notes_title)
        
        notes_text_box = ContentBox(orientation="horizontal", size_hint_y=0.7)
        notes_box.add_widget(notes_text_box)
        notes_text = FieldLabel(text=f"{notes}", valign="top", halign="left")
        notes_text.font_size = app.theme.small_size
        notes_text.color = app.theme.color_field_value
        notes_text_box.add_widget(notes_text)

        self.info_box.add_widget(event_details)



