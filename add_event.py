import math
import datetime
import logging
from uuid import uuid4
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock

from helpers import (get_difference_days, go_to_add_event, go_to_garden,
                      go_to_photo_gallery, go_to_are_you_sure, _coerce_to_date)
from data import GardenRepository, EventRepository, PhotoRepository
from services.plant_service import apply_event_side_effects
from effects import shake_and_flash
from constants import (
    EVENT_WATERING, EVENT_FEEDING, EVENT_LOG, EVENT_TOP,
    EVENT_PRUNE, EVENT_FLIP, EVENT_HARVEST,
)
from labels import FieldLabel, HintLabel
from boxes import ItemBox, WrapperBox, ContentBox, SpacerBox, RedBox, YellowBox, GreenBox, EventBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from ui_builders import create_water_fields, create_feeding_fields, create_nutrients_panel
from text_inputs import NumTextInput, MedTextInput, LargeTextInput
from plant_screen import BasePlantScreen
from custom_dropdown import CustomDropdown
from photo_widgets import PhotoViewPopup, PhotoPickerPopup, bytes_to_texture
import lang

LOG = logging.getLogger(__name__)


class AddEventScreen(BasePlantScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._selected_event_data = None
        self._editing_event = None  # holds event dict when in edit mode
        app = App.get_running_app()
        self._plant_set = False

        plant_details_screen, content_wrapper = self._build_sidebar_and_header(
            lang.SCREEN_TITLE_DETAILS,
        )

        info_box = WrapperBox(orientation="vertical", size_hint_x=1, size_hint_y=0.8)

        plant = self.plant or {}
        event = getattr(self, '_selected_event_data', None)
        # Don't abort construction if there's no selected event yet; render the
        # screen with defaults and allow `set_plant`/update to populate later.
        if not event:
            event = {}

        # Safely calculate days_passed and flip_day
        date_planted = plant.get("date_planted", "")
        days_to_flower = plant.get("days_to_flower")
        days_passed = get_difference_days(datetime.date.today(), date_planted)
        try:
            days_passed_val = int(days_passed) if days_passed is not None else 0
        except (ValueError, TypeError) as exc:
            LOG.warning("days_passed int conversion failed: %s", exc)
            days_passed_val = 0
        self.days_passed = days_passed_val
        self.days_passed_value.text = str(self.days_passed) if self.days_passed is not None else lang.DASH

        try:
            days_to_flower_val = int(days_to_flower) if days_to_flower is not None else 0
        except (ValueError, TypeError) as exc:
            LOG.warning("days_to_flower int conversion failed: %s", exc)
            days_to_flower_val = 0

        # Only calculate flip_day if both are valid
        flip_day = self.days_passed - days_to_flower_val - 14

        notes = str()
        water_volume = float()
        water_temperature = float()
        ph = float()
        ppm = int()

        grow_mix = float()
        root_mix = float()
        bloom_mix = float()
        bloom_boost = float()
        soil_boost = float()
        vit_boost = float()
        CalMag = float()
        myco_trico = bool()

        plant = event.get("plant", {})
        stage = plant.get("stage", "")


        days_stage = stage
        self.days_stage_value.text = f"{days_stage}" if days_stage is not None else lang.DASH

        environment = event.get("environment", {})

        # prepare realtime VPD update helpers
        self._air_temp_input = None
        self._rh_input = None
        self._vpd_label = None

        def update_vpd(*_):
            try:
                air = float(self._air_temp_input.text) if (self._air_temp_input and self._air_temp_input.text.strip() != "") else float(environment.get('air_temp_c', 0) or 0)
            except (ValueError, TypeError, AttributeError):
                air = 0.0
            try:
                rh = float(self._rh_input.text) if (self._rh_input and self._rh_input.text.strip() != "") else float(environment.get('rh_percent', 0) or 0)
            except (ValueError, TypeError, AttributeError):
                rh = 0.0
            vpd = self.calculate_vpd(air, rh)
            if self._vpd_label:
                self._vpd_label.text = f"{vpd:.2f} kPa"

        event_details = WrapperBox(orientation="vertical")

        event_title_row = WrapperBox(orientation="horizontal", size_hint_y=0.4)
        event_details.add_widget(event_title_row)

        date_and_type_box = WrapperBox(orientation="vertical", size_hint_x=0.3)
        event_title_row.add_widget(date_and_type_box)

        event_date_label_box =  ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(event_date_label_box)
        event_date_value = FieldLabel(text=f"{datetime.date.today()}", valign="middle", halign="left")
        event_date_value.color = app.theme.color_field_value
        event_date_value.font_size = app.theme.title_size
        event_date_label_box.add_widget(event_date_value)

        event_type_and_toggles_box = ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(event_type_and_toggles_box)

        event_type_value = CustomDropdown(
            selected="log",
            values=[EVENT_LOG, EVENT_WATERING, EVENT_FEEDING],
        )
        # Keep a reference so clear_fields can reset it directly
        self.event_type_dropdown = event_type_value
        event_type_value.font_size = app.theme.title_size
        event_type_value.color = app.theme.color_field_value
        event_type_and_toggles_box.add_widget(event_type_value)

        # Toggle buttons: Top / Prune / Flip (right of dropdown)
        toggle_box = ItemBox(orientation="horizontal", size_hint_x=0.6)
        self.top_toggle = ToggleButton(
            text=lang.TOGGLE_TOP, allow_no_selection=True,
        )
        self.prune_toggle = ToggleButton(
            text=lang.TOGGLE_PRUNE, allow_no_selection=True,
        )
        self.flip_toggle = ToggleButton(
            text=lang.TOGGLE_FLIP, allow_no_selection=True,
        )
        for tb in (self.top_toggle, self.prune_toggle, self.flip_toggle):
            toggle_box.add_widget(tb)
        event_type_and_toggles_box.add_widget(toggle_box)


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



        # Plant + env
        for i, (title, source, key, special) in enumerate(event_info_fields):
            if key == "soil_ph":
                value = float()
            else:
                value = int()
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

            if key == "leaf_color":
                value_label = CustomDropdown(
                    selected="normal",
                    values=["yellow", "light", "normal", "dark", "purple"],
                )
                self.leaf_color_dropdown = value_label
            elif key == "leaf_morphology":
                value_label = CustomDropdown(
                    selected="normal",
                    values=["normal", "duckfoot", "spiral phyllotaxy", "fasciation", "variegation", "albinism", "crinkled leaves", "single leaflet", "abc"],
                )
                self.leaf_morphology_dropdown = value_label
            elif key == "soil_moisture":
                value_label = CustomDropdown(
                    selected="moist",
                    values=["soaked", "wet", "moist", "dry", "dust"],
                )
                self.soil_moisture_dropdown = value_label
            elif key in ("air_temp_c", "rh_percent"):
                # numeric inputs for air temp and humidity; bind to update vpd
                hint = ""
                if isinstance(source, dict):
                    hint = source.get(key, "")
                value_label = NumTextInput(hint_text=str(hint))
                value_label.font_size = app.theme.subtitle_size
                value_label.color = app.theme.color_field_value
                if key == "air_temp_c":
                    self._air_temp_input = value_label
                    self._air_temp_input.hint_text = lang.HINT_AIR_TEMP_DEFAULT
                else:
                    self._rh_input = value_label
                    self._rh_input.hint_text = lang.HINT_RH_DEFAULT
                # bind if vpd label already exists
                if self._vpd_label:
                    value_label.bind(text=update_vpd)
                # ensure vpd recalculation when this input is created
                value_label.bind(text=lambda *a: update_vpd())
            elif key == "vpd_kpa":
                # display-only label; updated realtime from air/temp fields
                self._vpd_label = FieldLabel(text=lang.DASH, valign="middle", halign="left")
                self._vpd_label.font_size = app.theme.subtitle_size
                self._vpd_label.color = app.theme.color_field_value
                value_label = self._vpd_label
                # if inputs already exist bind them
                if self._air_temp_input:
                    self._air_temp_input.bind(text=update_vpd)
                if self._rh_input:
                    self._rh_input.bind(text=update_vpd)
                # compute initial value
                update_vpd()
            elif key == "light_schedule":
                value_label = CustomDropdown(
                    values=["24/0", "20/4", "18/6", "16/8", "14/10", "12/12"],
                )
                # Safely calculate flip_day to avoid TypeError
                date_planted = plant.get("date_planted", "")
                days_to_flower = plant.get("days_to_flower")
                days_passed = get_difference_days(datetime.date.today(), date_planted)
                try:
                    days_passed_val = int(days_passed) if days_passed is not None else 0
                except (ValueError, TypeError) as exc:
                    LOG.warning("days_passed int conversion failed: %s", exc)
                    days_passed_val = 0
                try:
                    days_to_flower_val = int(days_to_flower) if days_to_flower is not None else 0
                except (ValueError, TypeError) as exc:
                    LOG.warning("days_to_flower int conversion failed: %s", exc)
                    days_to_flower_val = 0
                flip_day = days_passed_val - days_to_flower_val - 14
                if flip_day <= 0:
                    # default to 12/12 if in flowering stage
                    value_label.selected = "12/12"
                else:
                    value_label.selected = "18/6"
                self.light_schedule_dropdown = value_label
            else:
                value_label = NumTextInput(hint_text=str(value))
                value_label.font_size = app.theme.subtitle_size
                value_label.color = app.theme.color_field_value
                # Patch: assign plant info inputs to self for data capture
                setattr(self, f"{key}_input", value_label)

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
        self.water_and_food_box = water_and_food_box

        # Render watering/feeding fields dynamically based on effective type
        event_type_value.bind(selected=self._on_event_type_changed)
        # initial render based on current selection
        self._render_water_food_fields(event_type_value.selected)


        right_column_box = WrapperBox(orientation="vertical", size_hint_x=0.33)
        main_data_column.add_widget(right_column_box)

        nutrients_box = create_nutrients_panel()  # interactive toggle mode
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
        notes_text = LargeTextInput(hint_text=lang.HINT_EVENT_NOTES)
        notes_text.font_size = app.theme.small_size
        notes_text.color = app.theme.color_field_value
        notes_text_box.add_widget(notes_text)
        self.notes_input = notes_text

        # -- Photo column (third column) --
        self._pending_photos = []  # list of (photo_id, plant_id, original_name, image_bytes)
        photo_column, self._photo_strip = self.build_photo_strip(
            on_select=self._on_photo_select,
            on_double_click=self._on_photo_double_click,
            gallery_callback=self._go_to_photo_gallery,
            add_callback=self._open_photo_picker,
            delete_callback=self._delete_selected_photo,
            gallery_text=lang.PHOTO_SHOW_GALLERY,
        )
        main_data_column.add_widget(photo_column)

        info_box.add_widget(event_details)

        content_wrapper.add_widget(info_box)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        # events scroll 
        scroll_events = ContentBox(orientation="horizontal", size_hint_y=0.3)

        add_event_box = WrapperBox(orientation="horizontal", size_hint_x=0.15)
        scroll_events.add_widget(add_event_box)
        add_event_button = ButtonYellow(text=lang.BUTTON_PLUS)
        add_event_button.font_size = app.theme.logo_size_1
        add_event_button.font_name = app.theme.font_logo_1
        def save_and_exit(instance):
            etype = self.event_type_dropdown.selected
            if self.on_event_save(self.plant, etype, event_date_value.text, notes_text.text):
                self.confirm_action()
        add_event_button.bind(on_release=save_and_exit)
        self.add_event_button = add_event_button
        add_event_box.add_widget(add_event_button)

        # Harvest button - right of the + button
        harvest_btn = ButtonRed(text=lang.LEGEND_HARVEST)
        harvest_btn.font_size = app.theme.subtitle_size
        def harvest_and_exit(instance):
            if self.on_event_save(self.plant, EVENT_HARVEST, event_date_value.text, notes_text.text):
                self.confirm_action()
        harvest_btn.bind(on_release=harvest_and_exit)
        self.harvest_button = harvest_btn
        add_event_box.add_widget(harvest_btn)

        content_wrapper.add_widget(scroll_events)
        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)


        buttons = ContentBox(size_hint_y=0.1)
        go_back_btn = ButtonRed(text=lang.BACK)
        go_back_btn.bind(on_release=self.on_cancel)
        buttons.add_widget(go_back_btn)
        content_wrapper.add_widget(buttons)

        plant_details_screen.add_widget(content_wrapper)
        spacer_right = SpacerBox(size_hint_x=0.1)
        plant_details_screen.add_widget(spacer_right)
        self.add_content(plant_details_screen)

    def validate(self):
        invalid = []
        # Check event type (dropdown only - toggles are independent flags)
        event_type = self.event_type_dropdown.selected if hasattr(self, 'event_type_dropdown') else 'log'

        # Harvest is handled by its own button and always valid.
        if event_type == EVENT_HARVEST:
            return invalid

        # Plant context is guaranteed by set_plant(); no need to check display labels.
        # Validate plant and environment fields for all event types except notes
        for w in self.walk():
            if isinstance(w, (NumTextInput, MedTextInput)) and w is not getattr(self, 'notes_input', None):
                if not (w.text or '').strip():
                    invalid.append(w)

        # Validate watering fields for both watering and feeding
        if event_type in (EVENT_WATERING, EVENT_FEEDING):
            for attr in ["water_volume_input", "water_temp_input", "ph_input", "ppm_input"]:
                w = getattr(self, attr, None)
                if w and not (w.text or '').strip():
                    invalid.append(w)

        # Validate feeding fields only for feeding
        if event_type == EVENT_FEEDING:
            for attr in ["grow_mix_input", "root_mix_input", "soil_boost_input", "vit_boost_input", "bloom_mix_input", "bloom_boost_input", "calmag_input"]:
                w = getattr(self, attr, None)
                if w and not (w.text or '').strip():
                    invalid.append(w)
            # At least one main nutrient must be filled
            found_nutrient = False
            for nutrient in ["n_input", "p_input", "k_input"]:
                if hasattr(self, nutrient) and getattr(self, nutrient).text.strip():
                    found_nutrient = True
            if not found_nutrient:
                for nutrient in ["n_input", "p_input", "k_input"]:
                    if hasattr(self, nutrient):
                        invalid.append(getattr(self, nutrient))
        return invalid
    
    def _end_validation(self, dt):
        self._is_validating = False
        
    def confirm_action(self):
        app = App.get_running_app()
        self.clear_fields()
        # Reload events in plant details screen
        plant_details_screen = app.screen.get_screen("plant_details")
        if hasattr(plant_details_screen, "_load_and_display_events"):
            plant_details_screen._load_and_display_events()
        app.screen.current = "plant_details"
        return app.screen
    
    def on_cancel(self, instance):
        go_to_are_you_sure(lang.MSG_CONFIRM_CANCEL_CHANGES,
                           lambda *_: self.confirm_action())

    def _get_effective_event_type(self):
        """Return the event type from the dropdown.

        Toggles (top/prune/flip) are independent flags stored alongside
        the event type - they no longer override the dropdown.
        """
        return self.event_type_dropdown.selected

    def _get_active_toggles(self):
        """Return a list of active toggle event types."""
        active = []
        if self.top_toggle.state == "down":
            active.append(EVENT_TOP)
        if self.prune_toggle.state == "down":
            active.append(EVENT_PRUNE)
        if self.flip_toggle.state == "down":
            active.append(EVENT_FLIP)
        return active

    def _on_event_type_changed(self, instance, value):
        """Dropdown changed - re-render water/food area."""
        self._render_water_food_fields(None, self.event_type_dropdown.selected)

    def clear_fields(self):
        for w in self.walk():
            if isinstance(w, (NumTextInput, MedTextInput, LargeTextInput)):
                w.text = ""
                continue
            if hasattr(w, 'state'):
                w.state = 'normal'
        if hasattr(self, 'event_type_dropdown'):
            self.event_type_dropdown.select_option('log')
        # Reset toggles
        for tb in ('top_toggle', 'prune_toggle', 'flip_toggle'):
            t = getattr(self, tb, None)
            if t:
                t.state = 'normal'
        if hasattr(self, 'leaf_color_dropdown'):
            self.leaf_color_dropdown.select_option('normal')
        if hasattr(self, 'leaf_morphology_dropdown'):
            self.leaf_morphology_dropdown.select_option('normal')
        if hasattr(self, 'soil_moisture_dropdown'):
            self.soil_moisture_dropdown.select_option('moist')
        if hasattr(self, 'fungi_dropdown'):
            self.fungi_dropdown.select_option('no')
        # Clear photo strip and pending photos
        if hasattr(self, '_photo_strip'):
            import hover_manager
            hover_manager.unregister_tree(self._photo_strip._grid)
            self._photo_strip._grid.clear_widgets()
            self._photo_strip._thumbnails.clear()
            self._photo_strip.selected_photo_id = ""
        self._pending_photos = []
        self._selected_photo_id = ""
        # Clear edit mode
        self._editing_event = None
        # Reset save button text
        app = App.get_running_app()
        if hasattr(self, 'add_event_button'):
            self.add_event_button.text = lang.BUTTON_PLUS
            self.add_event_button.font_size = app.theme.logo_size_1
            self.add_event_button.font_name = app.theme.font_logo_1

    def enter_edit_mode(self, event_data):
        """Pre-populate all fields from an existing event for editing."""
        if not event_data or not isinstance(event_data, dict):
            return
        self._editing_event = event_data
        app = App.get_running_app()

        # Update save button to indicate editing
        if hasattr(self, 'add_event_button'):
            self.add_event_button.text = lang.BUTTON_EDIT if hasattr(lang, 'BUTTON_EDIT') else "Save"
            self.add_event_button.font_size = app.theme.body_size
            self.add_event_button.font_name = app.theme.font_body

        # Event type (dropdown)
        etype = event_data.get("type", EVENT_LOG)
        if etype in (EVENT_LOG, EVENT_WATERING, EVENT_FEEDING):
            if hasattr(self, 'event_type_dropdown'):
                self.event_type_dropdown.select_option(etype)
        else:
            # Legacy events where type was top/prune/flip: default dropdown to log
            if hasattr(self, 'event_type_dropdown'):
                self.event_type_dropdown.select_option(EVENT_LOG)

        # Restore toggle states from flags (supports both new and legacy format)
        if event_data.get("topped") or etype == EVENT_TOP:
            self.top_toggle.state = "down"
        if event_data.get("pruned") or etype == EVENT_PRUNE:
            self.prune_toggle.state = "down"
        if event_data.get("flipped") or etype == EVENT_FLIP:
            self.flip_toggle.state = "down"

        # Notes
        if hasattr(self, 'notes_input'):
            self.notes_input.text = event_data.get("notes", "")

        # Plant info fields
        plant_info = event_data.get("plant", {})
        for key in ("plant_height", "num_nodes", "node_spacing", "main_stem_number"):
            w = getattr(self, f"{key}_input", None)
            if w and plant_info.get(key) is not None:
                w.text = str(plant_info[key])
        # Dropdowns
        for key, attr in (("leaf_color", "leaf_color_dropdown"), ("leaf_morphology", "leaf_morphology_dropdown")):
            dd = getattr(self, attr, None)
            val = plant_info.get(key)
            if dd and val:
                dd.select_option(str(val))

        # Environment fields
        env = event_data.get("environment", {})
        if self._air_temp_input and env.get("air_temp_c") is not None:
            self._air_temp_input.text = str(env["air_temp_c"])
        if self._rh_input and env.get("rh_percent") is not None:
            self._rh_input.text = str(env["rh_percent"])
        for key in ("soil_ph", "ppfd"):
            w = getattr(self, f"{key}_input", None)
            if w and env.get(key) is not None:
                w.text = str(env[key])
        sm = getattr(self, "soil_moisture_dropdown", None)
        if sm and env.get("soil_moisture"):
            sm.select_option(str(env["soil_moisture"]))
        ls = getattr(self, "light_schedule_dropdown", None)
        if ls and env.get("light_schedule"):
            ls.select_option(str(env["light_schedule"]))

        # Render water/food fields based on the dropdown selection
        dropdown_type = self.event_type_dropdown.selected if hasattr(self, 'event_type_dropdown') else EVENT_LOG
        self._render_water_food_fields(None, dropdown_type)

        # Water fields
        if dropdown_type in (EVENT_WATERING, EVENT_FEEDING):
            for attr, key in [("water_volume_input", "volume_l"), ("water_temp_input", "water_temp_c"),
                              ("ph_input", "ph"), ("ppm_input", "ppm")]:
                w = getattr(self, attr, None)
                if w and event_data.get(key) is not None:
                    w.text = str(event_data[key])

        # Feeding fields
        if dropdown_type == EVENT_FEEDING:
            feeding = event_data.get("feeding", {})
            feed_map = [
                ("grow_mix", "grow_mix_input"),
                ("root_mix", "root_mix_input"),
                ("bloom_mix", "bloom_mix_input"),
                ("bloom_boost", "bloom_boost_input"),
                ("soil_boost", "soil_boost_input"),
                ("vit_boost", "vit_boost_input"),
                ("CalMag", "calmag_input"),
            ]
            for data_key, input_attr in feed_map:
                w = getattr(self, input_attr, None)
                if w and feeding.get(data_key) is not None:
                    w.text = str(feeding[data_key])
            if hasattr(self, 'fungi_dropdown') and "myco_trico" in feeding:
                self.fungi_dropdown.select_option("yes" if feeding["myco_trico"] else "no")

        # Nutrient buttons (deficiencies/excess)
        deficiencies = plant_info.get("deficiencies", {})
        excess = plant_info.get("excess", {})
        nutrients = ["n", "p", "k", "ca", "mg", "s", "fe", "mn", "zn", "cu", "b", "mo"]
        for n in nutrients:
            for w in self.walk():
                if hasattr(w, 'group') and w.group == n and hasattr(w, 'state'):
                    if w.text == "+" and excess.get(n):
                        w.state = "down"
                    elif w.text == "-" and deficiencies.get(n):
                        w.state = "down"

        # Photos from existing event
        photo_ids = event_data.get("photos", [])
        if photo_ids and hasattr(self, '_photo_strip'):
            plant_id = str((self.plant or {}).get("plant_id") or (self.plant or {}).get("id") or "")
            for photo_id in photo_ids:
                try:
                    raw = PhotoRepository.load_photo_bytes(plant_id, photo_id)
                    if raw:
                        from photo_utils import generate_thumbnail
                        thumb_bytes = generate_thumbnail(raw)
                        texture = bytes_to_texture(thumb_bytes)
                        self._photo_strip.add_thumbnail(photo_id, plant_id, texture)
                except Exception:
                    LOG.exception("Failed to load photo %s for edit mode", photo_id)

    # load and show events
    def set_plant(self, plant: dict):
        if not plant or not isinstance(plant, dict):
            raise ValueError("set_plant must be called with a valid plant dict.")
        # Normalise: accept either "id" or "plant_id"
        pid = plant.get("plant_id") or plant.get("id")
        if not pid:
            raise ValueError("set_plant: plant dict must contain 'id' or 'plant_id'.")
        plant["plant_id"] = pid
        plant.setdefault("id", pid)
        self.plant = plant
        self._plant_set = True
        self._editing_event = None  # reset edit mode on new plant set
        self._update_ui()
        self._autofill_from_last_event(pid)
        self._update_flip_toggle_state(pid)
        self._update_harvest_button_state(pid)

    def _update_ui(self):
        super()._update_ui()
        app = App.get_running_app()
        self._prefill_light_schedule(app, self.plant or {})

    def _autofill_from_last_event(self, plant_id):
        """Pre-populate all editable fields from the last saved event."""
        try:
            existing = EventRepository.get(plant_id)
            events = existing.get("events", []) if existing else []
            if not events:
                return
            last = events[-1]

            # Plant info fields
            plant_info = last.get("plant", {})
            for key in ("plant_height", "num_nodes", "node_spacing", "main_stem_number"):
                w = getattr(self, f"{key}_input", None)
                if w and plant_info.get(key):
                    w.text = str(plant_info[key])
            # Dropdowns
            for key, attr in (("leaf_color", "leaf_color_dropdown"), ("leaf_morphology", "leaf_morphology_dropdown")):
                dd = getattr(self, attr, None)
                val = plant_info.get(key)
                if dd and val:
                    dd.select_option(str(val))

            # Environment fields
            env = last.get("environment", {})
            if self._air_temp_input and env.get("air_temp_c"):
                self._air_temp_input.text = str(env["air_temp_c"])
            if self._rh_input and env.get("rh_percent"):
                self._rh_input.text = str(env["rh_percent"])
            for key in ("soil_ph", "ppfd"):
                w = getattr(self, f"{key}_input", None)
                if w and env.get(key):
                    w.text = str(env[key])
            sm = getattr(self, "soil_moisture_dropdown", None)
            if sm and env.get("soil_moisture"):
                sm.select_option(str(env["soil_moisture"]))
            ls = getattr(self, "light_schedule_dropdown", None)
            if ls and env.get("light_schedule"):
                ls.select_option(str(env["light_schedule"]))
        except Exception:
            LOG.exception("Failed to autofill from last event")

    def _update_flip_toggle_state(self, plant_id):
        """Disable flip toggle if a flip event already exists in history."""
        try:
            existing = EventRepository.get(plant_id)
            events = existing.get("events", []) if existing else []
            has_flip = any(
                isinstance(e, dict) and e.get("type") == EVENT_FLIP
                for e in events
            )
            if hasattr(self, 'flip_toggle'):
                self.flip_toggle.disabled = has_flip
                if has_flip:
                    self.flip_toggle.state = "normal"
        except Exception:
            LOG.exception("Failed to check flip toggle state")

    def _update_harvest_button_state(self, plant_id):
        """Disable harvest button if a harvest event already exists."""
        try:
            existing = EventRepository.get(plant_id)
            events = existing.get("events", []) if existing else []
            has_harvest = any(
                isinstance(e, dict) and e.get("type") == EVENT_HARVEST
                for e in events
            )
            if hasattr(self, 'harvest_button'):
                self.harvest_button.disabled = has_harvest
        except Exception:
            LOG.exception("Failed to check harvest button state")

    def _prefill_light_schedule(self, app, plant):
        """Pre-select light_schedule_dropdown from garden config.

        For indoor gardens: use the stored light_schedule [on, off].
        For outdoor gardens with location: compute today's daylight via astral.
        Falls back to the existing flip_day heuristic if no garden data.
        """
        dropdown = getattr(self, 'light_schedule_dropdown', None)
        if dropdown is None:
            return

        garden_id = getattr(app, 'current_garden_id', None)
        garden = GardenRepository.get(garden_id) if garden_id else None

        if garden:
            sched = garden.get("light_schedule", [])
            location = garden.get("location") or {}
            garden_type = garden.get("type", "indoor")

            if garden_type == "outdoor" and location.get("lat") is not None:
                # Outdoor: compute today's daylight
                try:
                    from add_garden import _daylight_hours
                    hours = _daylight_hours(
                        location["lat"], location["lon"], location["tz"],
                    )
                    on = round(hours)
                    off = 24 - on
                    label = f"{on}/{off}"
                    if label in [b.text for b in dropdown.dropdown.container.children] if hasattr(dropdown, 'dropdown') else []:
                        dropdown.select_option(label)
                    else:
                        dropdown.select_option(f"{on}/{off}")
                except Exception:
                    LOG.exception("Failed to compute outdoor daylight")
                return

            if sched and len(sched) >= 2:
                on, off = int(sched[0]), int(sched[1])
                label = f"{on}/{off}"
                dropdown.select_option(label)
                return

        # Fallback: use flip_day heuristic (existing behaviour)
        # (already set during __init__)

    def _render_water_food_fields(self, instance, value=None):
        # Clear previous references to ensure validation works
        for attr in [
            'water_volume_input', 'water_temp_input', 'ph_input', 'ppm_input',
            'grow_mix_input', 'root_mix_input', 'soil_boost_input', 'vit_boost_input',
            'bloom_mix_input', 'bloom_boost_input', 'calmag_input',
        ]:
            if hasattr(self, attr):
                delattr(self, attr)
        # instance/value signature supports being bound (instance, value)
        if value is None:
            selection = instance
        else:
            selection = value

        box = getattr(self, "water_and_food_box", None)
        if box is None:
            return
        box.clear_widgets()

        if selection in (EVENT_WATERING, EVENT_FEEDING):
            water_row, water_refs = create_water_fields()
            box.add_widget(water_row)
            for attr, widget in water_refs.items():
                setattr(self, attr, widget)

            if selection == EVENT_FEEDING:
                feeding_container, feeding_refs = create_feeding_fields()
                box.add_widget(feeding_container)
                for attr, widget in feeding_refs.items():
                    setattr(self, attr, widget)
                spacer = SpacerBox(size_hint_y=0.34)
                box.add_widget(spacer)
            else:
                spacer = SpacerBox(size_hint_y=0.75)
                box.add_widget(spacer)
        else:
            # For log - show empty space
            spacer = SpacerBox()
            box.add_widget(spacer)

    def calculate_vpd(self, air_temp_c, rh_percent):
        es = 0.6108 * math.exp((17.27 * air_temp_c) / (air_temp_c + 237.3))  # Saturation vapor pressure (kPa)
        vpd = (1 - rh_percent / 100.0) * es  # Vapor Pressure Deficit (kPa)
        vpd = f"{vpd:.2f}"
        return float(vpd)
        
    def on_event_save(self, plant, event_type=None, event_date=None, notes=None):
        try:
            if not getattr(self, '_plant_set', False):
                LOG.error("set_plant was not called before on_event_save")
                return False
            app = App.get_running_app()
            # Validate
            invalid = self.validate()
            if invalid:
                for widget in invalid:
                    shake_and_flash(widget)
                return False

            # Determine event type from dropdown (toggles stored separately)
            event_type = event_type or self._get_effective_event_type()
            today = datetime.date.today().isoformat()
            if notes is None:
                notes = self.notes_input.text if hasattr(self, 'notes_input') else ""
            event_date = event_date or today

            # Find plant_id (normalised by set_plant)
            plant_id = self.plant.get("plant_id") or self.plant.get("id")
            if not plant_id:
                LOG.error("No plant_id found on plant dict")
                return False

            # Edit mode: reuse existing event id; otherwise generate a new one
            is_edit = self._editing_event is not None
            if is_edit:
                event_id = self._editing_event.get("id", "evt-0")
            else:
                # Generate event id from existing events
                existing = EventRepository.get(plant_id)
                events = existing.get("events", []) if existing else []
                if events and "id" in events[-1]:
                    try:
                        num = int(events[-1]["id"].split("-")[-1]) + 1
                    except (ValueError, TypeError, IndexError) as exc:
                        LOG.warning("Failed to parse event ID '%s': %s", events[-1].get("id"), exc)
                        num = len(events)
                else:
                    num = 0
                event_id = f"evt-{num}"

            # Water/food value helpers
            def get_num_input(attr):
                w = getattr(self, attr, None)
                if w and hasattr(w, "text"):
                    try:
                        return float(w.text)
                    except (ValueError, TypeError) as exc:
                        LOG.warning("Numeric input conversion failed for %s: %s", attr, exc)
                        return 0.0
                return 0.0

            # Water/feeding fields
            if event_type == "log":
                volume_l = 0.0
                water_temp_c = 0.0
                ph = 0.0
                ppm = 0
            else:
                volume_l = get_num_input("water_volume_input")
                water_temp_c = get_num_input("water_temp_input")
                ph = get_num_input("ph_input")
                ppm = int(get_num_input("ppm_input"))

            # Feeding fields
            feeding = {}
            if event_type == EVENT_FEEDING:
                feed_map = [
                    ("grow_mix", "grow_mix_input"),
                    ("root_mix", "root_mix_input"),
                    ("bloom_mix", "bloom_mix_input"),
                    ("bloom_boost", "bloom_boost_input"),
                    ("soil_boost", "soil_boost_input"),
                    ("vit_boost", "vit_boost_input"),
                    ("CalMag", "calmag_input"),
                ]
                for data_key, input_attr in feed_map:
                    feeding[data_key] = get_num_input(input_attr)
                feeding["myco_trico"] = (self.fungi_dropdown.selected == "yes") if hasattr(self, "fungi_dropdown") else False
            else:
                feeding = {k: 0.0 for k in ["grow_mix", "root_mix", "bloom_mix", "bloom_boost", "soil_boost", "vit_boost", "CalMag"]}
                feeding["myco_trico"] = False

            # Plant info
            def get_dropdown_val(attr, default):
                w = getattr(self, attr, None)
                if w and hasattr(w, "selected"):
                    return w.selected
                return default

            plant_info = {
                "plant_height": get_num_input("plant_height_input"),
                "num_nodes": int(get_num_input("num_nodes_input")),
                "node_spacing": get_num_input("node_spacing_input"),
                "main_stem_number": int(get_num_input("main_stem_number_input")),
                "leaf_color": get_dropdown_val("leaf_color_dropdown", "normal"),
                "leaf_morphology": get_dropdown_val("leaf_morphology_dropdown", "normal"),
            }
            # Deficiencies/excess from nutrient buttons
            nutrients = ["n", "p", "k", "ca", "mg", "s", "fe", "mn", "zn", "cu", "b", "mo"]
            deficiencies = {}
            excess = {}
            for n in nutrients:
                plus = False
                minus = False
                for w in self.walk():
                    if hasattr(w, "group") and w.group == n:
                        if hasattr(w, "state"):
                            if w.text == "+" and w.state == "down":
                                plus = True
                            elif w.text == "-" and w.state == "down":
                                minus = True
                deficiencies[n] = minus
                excess[n] = plus
            plant_info["deficiencies"] = deficiencies
            plant_info["excess"] = excess
            plant_info["stage"] = plant.get("stage", "")

            # Environment info
            def get_env_num(attr, fallback=0.0):
                w = getattr(self, attr, None)
                if w and hasattr(w, "text"):
                    try:
                        return float(w.text)
                    except Exception:
                        return fallback
                return fallback

            air_temp_c = get_env_num("_air_temp_input")
            rh_percent = get_env_num("_rh_input")
            vpd_kpa = self.calculate_vpd(air_temp_c, rh_percent)
            environment = {
                "air_temp_c": air_temp_c,
                "rh_percent": rh_percent,
                "soil_moisture": get_dropdown_val("soil_moisture_dropdown", "moist"),
                "soil_ph": get_env_num("soil_ph_input"),
                "vpd_kpa": vpd_kpa,
                "ppfd": get_env_num("ppfd_input"),
                "light_schedule": plant.get("light_schedule", "")
            }

            # Collect active toggle flags
            active_toggles = self._get_active_toggles()

            # Compose event
            pending_photo_ids = [p[0] for p in getattr(self, '_pending_photos', [])]
            event = {
                "id": event_id,
                "ts": event_date,
                "type": event_type,
                "notes": notes,
                "topped": EVENT_TOP in active_toggles,
                "pruned": EVENT_PRUNE in active_toggles,
                "flipped": EVENT_FLIP in active_toggles,
                "volume_l": volume_l,
                "water_temp_c": water_temp_c,
                "ph": ph,
                "ppm": ppm,
                "feeding": feeding,
                "plant": plant_info,
                "environment": environment,
            }
            if pending_photo_ids:
                event["photos"] = pending_photo_ids
            elif is_edit and self._editing_event.get("photos"):
                # Preserve existing photos when editing unless new ones were added
                event["photos"] = self._editing_event["photos"]

            # Save via repository (handles encryption, atomic writes, caching)
            if is_edit:
                ok = EventRepository.update_event(plant_id, event_id, event)
                if ok:
                    LOG.info("Event %s updated for plant %s", event_id, plant_id)
                else:
                    LOG.error("Failed to update event %s for plant %s", event_id, plant_id)
            else:
                ok = EventRepository.add_event(plant_id, event)
                if ok:
                    LOG.info("Event %s saved for plant %s", event_id, plant_id)
                else:
                    LOG.error("Failed to save event %s for plant %s", event_id, plant_id)
            if ok:
                # Persist pending photos
                garden_id = str(app.current_garden_id or "")
                for photo_id, p_plant_id, orig_name, img_bytes in getattr(self, '_pending_photos', []):
                    PhotoRepository.attach(
                        p_plant_id, event_id, garden_id,
                        photo_id, img_bytes, orig_name,
                    )
                self._pending_photos = []
                # Post-save side-effects for special event types (skip on edit)
                if not is_edit:
                    apply_event_side_effects(garden_id, plant_id, event_type)
                    # Apply side-effects for each active toggle
                    for toggle_type in active_toggles:
                        apply_event_side_effects(garden_id, plant_id, toggle_type)
            return ok
        except Exception:
            LOG.exception("Exception in on_event_save")
            return False

    def _on_photo_select(self, photo_id):
        self._selected_photo_id = photo_id

    def _delete_selected_photo(self):
        """Delete the currently selected photo.

        Handles both pending (unsaved) and already-persisted photos.
        """
        if not self._selected_photo_id:
            return
        app = App.get_running_app()
        photo_id = self._selected_photo_id

        # Check if it's a pending (not yet saved) photo
        pending = getattr(self, '_pending_photos', [])
        for i, (pid, plid, name, img_bytes) in enumerate(pending):
            if pid == photo_id:
                pending.pop(i)
                self._photo_strip.remove_thumbnail(photo_id)
                self._selected_photo_id = ""
                return

        # Persisted photo - confirm before deleting
        def _do_delete():
            meta = PhotoRepository.get_meta(photo_id)
            if not meta:
                app.screen.current = "add_event"
                return
            plant_id = meta.get("plant_id", "")
            PhotoRepository.detach(plant_id, photo_id)
            self._photo_strip.remove_thumbnail(photo_id)
            self._selected_photo_id = ""
            app.screen.current = "add_event"

        go_to_are_you_sure(lang.MSG_CONFIRM_DELETE_PHOTO, _do_delete)

    def _on_photo_double_click(self, photo_id, plant_id):
        # For pending photos, find the bytes in the pending list (no navigation)
        for pid, plid, name, img_bytes in getattr(self, '_pending_photos', []):
            if pid == photo_id:
                popup = PhotoViewPopup(image_bytes=img_bytes)
                popup.open()
                return
        # Fallback to loaded photo - no gallery navigation in add_event
        raw = PhotoRepository.load_photo_bytes(plant_id, photo_id)
        if raw:
            popup = PhotoViewPopup(image_bytes=raw)
            popup.open()

    def _go_to_photo_gallery(self):
        go_to_photo_gallery(None, self.plant or {})

    def _open_photo_picker(self):
        plant = self.plant or {}
        plant_id = str(plant.get("plant_id") or plant.get("id") or "")
        if not plant_id:
            return

        def _on_file_selected(filepath):
            try:
                image_bytes = filepath.read_bytes()
            except Exception:
                return

            from photo_utils import validate_image, generate_thumbnail
            if not validate_image(image_bytes):
                return

            photo_id = str(uuid4())
            self._pending_photos.append((photo_id, plant_id, filepath.name, image_bytes))

            # Generate thumbnail and add to strip
            try:
                thumb_bytes = generate_thumbnail(image_bytes)
                texture = bytes_to_texture(thumb_bytes)
                self._photo_strip.add_thumbnail(photo_id, plant_id, texture)
            except Exception:
                LOG.exception("Failed to add thumbnail preview")

        PhotoPickerPopup(on_file_selected=_on_file_selected).open()