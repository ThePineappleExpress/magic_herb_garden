import datetime
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from uuid import uuid4

from helpers import get_difference_days, go_to_add_event, go_to_garden, go_to_timeline
from data import EventRepository, PhotoRepository
from constants import (
    EVENT_WATERING, EVENT_FEEDING, EVENT_PLANTING, EVENT_HARVEST,
)
from labels import TitleLabel, FieldLabel, HintLabel, ListTitleLabel, LogoLabel2
from boxes import ItemBox, WrapperBox, ContentBox, SpacerBox, RedBox, YellowBox, GreenBox, EventBox, SelectableBoxLayout, SelectableEventBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow, ButtonTransparent
from text_inputs import NumTextInput, MedTextInput, LargeTextInput
from screens import BaseScreen
from ui_builders import create_water_fields, create_feeding_fields, create_nutrients_panel
from photo_widgets import PhotoStrip, PhotoViewPopup, PhotoPickerPopup, bytes_to_texture
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
        add_event_box = WrapperBox(orientation="vertical", size_hint_x=0.1)
        scroll_events.add_widget(add_event_box)

        # "+" button - always creates a new event
        add_event_button = ButtonYellow(text=lang.BUTTON_PLUS)
        add_event_button.font_size = app.theme.logo_size_1
        add_event_button.font_name = app.theme.font_logo_1
        def safe_go_to_add_event(instance):
            plant = self.plant or {}
            if 'plant_id' not in plant and 'id' in plant:
                plant = dict(plant)
                plant['plant_id'] = plant['id']
            go_to_add_event(self, plant)
        add_event_button.bind(on_release=safe_go_to_add_event)
        self.add_event_button = add_event_button
        add_event_box.add_widget(add_event_button)

        # "Edit" button - edits the currently selected event
        edit_event_button = ButtonGreen(
            text=lang.BUTTON_EDIT if hasattr(lang, 'BUTTON_EDIT') else "Edit",
        )
        edit_event_button.font_size = app.theme.body_size
        edit_event_button.font_name = app.theme.font_body
        edit_event_button.disabled = True  # enabled when an event is selected
        def safe_go_to_edit_event(instance):
            event_data = getattr(self, '_selected_event_data', None)
            if not event_data:
                return
            plant = self.plant or {}
            if 'plant_id' not in plant and 'id' in plant:
                plant = dict(plant)
                plant['plant_id'] = plant['id']
            go_to_add_event(self, plant)
            add_event_screen = app.screen.get_screen('add_event')
            add_event_screen.enter_edit_mode(event_data)
        edit_event_button.bind(on_release=safe_go_to_edit_event)
        self.edit_event_button = edit_event_button
        add_event_box.add_widget(edit_event_button)
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
        self.name_label.text = " | ".join([plant.get("seedbank", ""), self.genes])
        
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
        # Enable edit button when an event is selected
        if hasattr(self, 'edit_event_button'):
            self.edit_event_button.disabled = False
        self.selected_event_view()

    def _load_and_display_events(self):
        import hover_manager
        hover_manager.unregister_tree(self.events_container)
        self.events_container.clear_widgets()
        self._selected_event_item = None

        plant = self.plant or {}
        plant_id = plant.get("id")
        if not plant_id:
            return

        data = EventRepository.get(str(plant_id))
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

        # Disable add-event if plant has been harvested
        app = App.get_running_app()
        has_harvest = any(
            isinstance(e, dict) and e.get("type") == EVENT_HARVEST
            for e in events
        )
        if hasattr(self, 'add_event_button'):
            self.add_event_button.disabled = has_harvest
        # Edit button starts disabled; gets enabled when user selects an event
        if hasattr(self, 'edit_event_button'):
            self.edit_event_button.disabled = True

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
        import hover_manager
        hover_manager.unregister_tree(self.info_box)
        self.info_box.clear_widgets()
        app = App.get_running_app()
        plant = self.plant or {}
        event = getattr(self, '_selected_event_data', None) 
        if not event:
            return
        event_date = event.get("ts") or ""
        formatter = []
        split_date = event_date.split("-") if event_date else []
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
            ("Height", plant_obs, "plant_height", False),
            ("Nodes", plant_obs, "num_nodes", False),
            ("Spacing", plant_obs, "node_spacing", False),
            ("Main Stems", plant_obs, "main_stem_number", False),
            ("Color", plant_obs, "leaf_color", False),
            ("Morphology", plant_obs, "leaf_morphology", False),
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

        water_and_food_box = WrapperBox(orientation="vertical", size_hint_x=0.33)
        main_data_column.add_widget(water_and_food_box)

        # Watering/Feeding fields (no units, looped)
        if event_type in (EVENT_WATERING, EVENT_FEEDING):
            water_row, _ = create_water_fields(values={
                "volume": water_volume,
                "temp": water_temperature,
                "ph": ph,
                "ppm": ppm,
            })
            water_and_food_box.add_widget(water_row)
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)

        # Feeding fields (looped, special logic for stage)
        if event_type == EVENT_FEEDING:
            feeding_container, _ = create_feeding_fields(
                values={
                    "grow_mix": grow_mix,
                    "root_mix": root_mix,
                    "soil_boost": soil_boost,
                    "vit_boost": vit_boost,
                    "bloom_mix": bloom_mix,
                    "bloom_boost": bloom_boost,
                    "calmag": CalMag,
                    "fungi": myco_trico,
                },
                stage=stage,
            )
            water_and_food_box.add_widget(feeding_container)
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)

        right_column_box = WrapperBox(orientation="vertical", size_hint_x=0.33)
        main_data_column.add_widget(right_column_box)

        nutrients_box = create_nutrients_panel(
            plant_data=plant_obs,
            get_nutrient_fn=self.get_nutrient,
        )
        right_column_box.add_widget(nutrients_box)

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
        spacer = SpacerBox(size_hint_x=0.01)
        main_data_column.add_widget(spacer)
        # -- Photo column (third column) --
        photo_column_box = WrapperBox(orientation="vertical", size_hint_x=0.33)
        main_data_column.add_widget(photo_column_box)

        photo_title_box = ContentBox(orientation="horizontal", size_hint_y=0.1)
        photo_column_box.add_widget(photo_title_box)
        photo_title = FieldLabel(text=lang.PHOTOS_TITLE, valign="bottom", halign="left")
        photo_title.color = app.theme.color_field_label
        photo_title.font_size = app.theme.subtitle_size
        photo_title_box.add_widget(photo_title)

        event_id = event.get("id", "")
        plant_id = str(plant.get("id") or plant.get("plant_id") or "")
        photo_metas = PhotoRepository.list_for_event(event_id, plant_id=plant_id) if event_id else []

        self._photo_strip = PhotoStrip(
            size_hint_y=0.7,
            on_select=self._on_photo_select,
            on_double_click=self._on_photo_double_click,
        )
        self._photo_strip.set_photos(
            photo_metas,
            load_thumb_fn=PhotoRepository.load_thumb_bytes,
        )
        photo_column_box.add_widget(self._photo_strip)

        photo_buttons_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        photo_column_box.add_widget(photo_buttons_box)

        view_gallery_btn = ButtonGreen(text=lang.PHOTO_VIEW_GALLERY, size_hint_x=0.34)
        view_gallery_btn.font_size = app.theme.small_size
        view_gallery_btn.bind(on_release=lambda *_: self._go_to_photo_gallery())
        photo_buttons_box.add_widget(view_gallery_btn)

        add_photo_btn = ButtonYellow(text=lang.PHOTO_ADD, size_hint_x=0.33)
        add_photo_btn.font_size = app.theme.small_size
        add_photo_btn.bind(on_release=lambda *_: self._open_file_picker())
        photo_buttons_box.add_widget(add_photo_btn)

        delete_photo_btn = ButtonRed(text=lang.PHOTO_DELETE, size_hint_x=0.33)
        delete_photo_btn.font_size = app.theme.small_size
        delete_photo_btn.bind(on_release=lambda *_: self._delete_selected_photo())
        photo_buttons_box.add_widget(delete_photo_btn)

        self.info_box.add_widget(event_details)

    def _on_photo_select(self, photo_id):
        """Track the currently selected photo in the event strip."""
        self._selected_photo_id = photo_id

    def _delete_selected_photo(self):
        """Delete the currently selected photo after confirmation."""
        if not self._selected_photo_id:
            return
        app = App.get_running_app()
        photo_id = self._selected_photo_id

        def _do_delete():
            meta = PhotoRepository.get_meta(photo_id)
            if not meta:
                app.screen.current = "plant_details"
                return
            plant_id = meta.get("plant_id", "")
            PhotoRepository.detach(plant_id, photo_id)
            self._photo_strip.remove_thumbnail(photo_id)
            self._selected_photo_id = ""
            app.screen.current = "plant_details"

        app.previous_screen = "plant_details"
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.prompt_text = lang.MSG_CONFIRM_DELETE_PHOTO
        are_you_sure.confirm_callback = _do_delete
        app.screen.current = "are_you_sure"

    def _on_photo_double_click(self, photo_id, plant_id):
        """Open full-size photo viewer on double-click (same-event photos)."""
        raw = PhotoRepository.load_photo_bytes(plant_id, photo_id)
        if raw:
            # Build photo list from the current event's photos
            event = getattr(self, '_selected_event_data', None)
            photo_list = []
            current_index = 0
            if event:
                event_id = event.get("id", "")
                if event_id:
                    metas = PhotoRepository.list_for_event(event_id, plant_id=plant_id)
                    photo_list = [(m["id"], m["plant_id"]) for m in metas]
                    for i, (pid, _) in enumerate(photo_list):
                        if pid == photo_id:
                            current_index = i
                            break
            popup = PhotoViewPopup(
                image_bytes=raw,
                photo_list=photo_list,
                current_index=current_index,
            )
            popup.open()

    def _go_to_photo_gallery(self):
        """Navigate to the per-plant photo gallery screen."""
        app = App.get_running_app()
        plant = self.plant or {}
        app.previous_screen = "plant_details"
        gallery = app.screen.get_screen("photo_gallery")
        gallery.set_plant(plant)
        app.screen.current = "photo_gallery"

    def _open_file_picker(self):
        """Open a file picker to attach a photo to the current event."""
        app = App.get_running_app()
        event = getattr(self, '_selected_event_data', None)
        plant = self.plant or {}
        if not event or not plant.get("id"):
            return

        def _on_file_selected(filepath):
            try:
                image_bytes = filepath.read_bytes()
            except Exception:
                return
            photo_id = str(uuid4())
            plant_id = str(plant["id"])
            event_id = str(event["id"])
            garden_id = str(app.current_garden_id or "")

            ok = PhotoRepository.attach(
                plant_id, event_id, garden_id,
                photo_id, image_bytes, filepath.name,
            )
            if ok:
                # Add photo ID to event's photos list
                photos = event.setdefault("photos", [])
                photos.append(photo_id)
                EventRepository.save(plant_id, {
                    "plant_id": plant_id,
                    "events": EventRepository.get(plant_id).get("events", []),
                })
                # Refresh the view
                self.selected_event_view()

        PhotoPickerPopup(on_file_selected=_on_file_selected).open()
