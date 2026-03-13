"""add_garden.py - New garden creation screen."""

import json
import logging
import os
from datetime import date
from uuid import uuid4

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.togglebutton import ToggleButton

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox
from buttons import ButtonGreen, ButtonRed
from custom_dropdown import CustomDropdown
from effects import shake_and_flash
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from text_inputs import MedTextInput
from ui_builders import create_initial_layout
import lang
import storage

LOG = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Location data (continent → country → [city, lat, lon, tz])
# ---------------------------------------------------------------------------
LOCATIONS_FILE = os.path.join(os.path.dirname(__file__), "bin", "db", "locations.json")

def _load_locations():
    try:
        with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        LOG.exception("Failed to load locations.json")
        return {}

LOCATIONS = _load_locations()

# ---------------------------------------------------------------------------
# Astral daylight helper
# ---------------------------------------------------------------------------
def _daylight_hours(lat, lon, tz_name, for_date=None):
    """Return hours of daylight for the given location and date."""
    try:
        from astral import LocationInfo
        from astral.sun import sun
        loc = LocationInfo("city", "region", tz_name, lat, lon)
        s = sun(loc.observer, date=for_date or date.today())
        return round((s["sunset"] - s["sunrise"]).total_seconds() / 3600, 1)
    except Exception:
        LOG.exception("astral daylight calculation failed")
        return 12.0


class AddGardenScreen(BaseScreen):

    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        app = App.get_running_app()
        title_text = lang.SCREEN_TITLE_ADD_GARDEN.format(color=TitleLabel().hex_color)
        screen_wrapper, layout = create_initial_layout(
            self, app, title_text=title_text, left_size=0.1,
            show_day_box=False, show_info_header=False,
        )

        layout.add_widget(WrapperBox(size_hint_y=0.5))

        # Garden name
        name_row = ContentBox(orientation="horizontal")
        name_row.add_widget(FieldLabel(text=lang.GARDEN_NAME_LABEL, size_hint_x=0.3))
        self.name_input = MedTextInput(hint_text=lang.HINT_GARDEN_NAME)
        name_row.add_widget(self.name_input)
        layout.add_widget(name_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # Garden type (Indoor / Outdoor)
        type_row = ContentBox(orientation="horizontal")
        type_row.add_widget(FieldLabel(text=lang.GARDEN_TYPE_LABEL, size_hint_x=0.3))
        type_box = ItemBox(orientation="horizontal")
        self.indoor_btn = ToggleButton(
            text=lang.GARDEN_TYPE_INDOOR, group="garden_type",
            allow_no_selection=False, state="down",
        )
        self.outdoor_btn = ToggleButton(
            text=lang.GARDEN_TYPE_OUTDOOR, group="garden_type",
            allow_no_selection=False,
        )
        self.indoor_btn.bind(state=self._on_type_toggle)
        self.outdoor_btn.bind(state=self._on_type_toggle)
        type_box.add_widget(self.indoor_btn)
        type_box.add_widget(self.outdoor_btn)
        type_row.add_widget(type_box)
        layout.add_widget(type_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # ── Dynamic section container (swapped between indoor/outdoor) ──
        self._dynamic_box = WrapperBox(orientation="vertical")
        layout.add_widget(self._dynamic_box)

        # ── Build indoor widgets (kept as attributes, added/removed dynamically) ──
        self._build_indoor_widgets()

        # ── Build outdoor widgets ──
        self._build_outdoor_widgets()

        # Show indoor by default
        self._show_indoor()

        layout.add_widget(SpacerBox(size_hint_y=0.04))

        # Buttons
        btn_row = WrapperBox(orientation="horizontal")
        btn_row.add_widget(WrapperBox())

        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        cancel_btn.bind(on_press=self._on_cancel)
        btn_row.add_widget(cancel_btn)

        save_btn = ButtonGreen(text=lang.BUTTON_SAVE)
        save_btn.bind(on_press=self._on_save)
        btn_row.add_widget(save_btn)

        layout.add_widget(btn_row)
        layout.add_widget(WrapperBox(size_hint_y=0.5))

        screen_wrapper.add_widget(layout)
        screen_wrapper.add_widget(SpacerBox(size_hint_x=0.1))

    # ── Indoor widgets ─────────────────────────────────────────────────────

    def _build_indoor_widgets(self):
        """Create indoor-specific widgets (light type, wattage, schedule)."""
        self._indoor_rows = []

        # Light type
        light_row = ContentBox(orientation="horizontal")
        light_row.add_widget(FieldLabel(text=lang.LIGHT_TYPE_LABEL, size_hint_x=0.3))
        light_box = ItemBox(orientation="horizontal")
        self.led_btn = ToggleButton(text=lang.LIGHT_LED, group="light_type", allow_no_selection=True)
        self.hps_btn = ToggleButton(text=lang.LIGHT_HPS, group="light_type", allow_no_selection=True)
        self.cfl_btn = ToggleButton(text=lang.LIGHT_CFL, group="light_type", allow_no_selection=True)
        light_box.add_widget(self.led_btn)
        light_box.add_widget(self.hps_btn)
        light_box.add_widget(self.cfl_btn)
        light_row.add_widget(light_box)
        self._indoor_rows.append(light_row)

        self._indoor_rows.append(SpacerBox(size_hint_y=0.02))

        # Wattage
        watt_row = ContentBox(orientation="horizontal")
        watt_row.add_widget(FieldLabel(text=lang.LIGHT_WATTAGE_LABEL, size_hint_x=0.3))
        self.wattage_input = MedTextInput(hint_text=lang.HINT_LIGHT_WATTAGE, input_filter="int")
        watt_row.add_widget(self.wattage_input)
        self._indoor_rows.append(watt_row)

        self._indoor_rows.append(SpacerBox(size_hint_y=0.02))

        # Light schedule with /x live label
        sched_row = ContentBox(orientation="horizontal")
        sched_row.add_widget(FieldLabel(text=lang.LIGHT_SCHEDULE_LABEL, size_hint_x=0.3))
        sched_input_box = ItemBox(orientation="horizontal")
        self.light_hours_input = MedTextInput(
            hint_text=lang.HINT_LIGHT_HOURS, input_filter="int",
            size_hint_x=0.5,
        )
        self.light_hours_input.bind(text=self._on_light_hours_text)
        sched_input_box.add_widget(self.light_hours_input)
        self._light_off_label = FieldLabel(text="/ —", size_hint_x=0.5)
        sched_input_box.add_widget(self._light_off_label)
        sched_row.add_widget(sched_input_box)
        self._indoor_rows.append(sched_row)

    # ── Outdoor widgets ────────────────────────────────────────────────────

    def _build_outdoor_widgets(self):
        """Create outdoor-specific widgets (continent → country → city cascading dropdowns)."""
        self._outdoor_rows = []

        # Continent
        continent_row = ContentBox(orientation="horizontal")
        continent_row.add_widget(FieldLabel(text=lang.CONTINENT_LABEL, size_hint_x=0.3))
        continents = sorted(LOCATIONS.keys())
        self.continent_dropdown = CustomDropdown(options=continents)
        self.continent_dropdown.bind(selected=self._on_continent_selected)
        continent_row.add_widget(self.continent_dropdown)
        self._outdoor_rows.append(continent_row)

        self._outdoor_rows.append(SpacerBox(size_hint_y=0.02))

        # Country
        country_row = ContentBox(orientation="horizontal")
        country_row.add_widget(FieldLabel(text=lang.COUNTRY_LABEL, size_hint_x=0.3))
        self.country_dropdown = CustomDropdown(options=[])
        self.country_dropdown.bind(selected=self._on_country_selected)
        country_row.add_widget(self.country_dropdown)
        self._outdoor_rows.append(country_row)

        self._outdoor_rows.append(SpacerBox(size_hint_y=0.02))

        # City
        city_row = ContentBox(orientation="horizontal")
        city_row.add_widget(FieldLabel(text=lang.CITY_LABEL, size_hint_x=0.3))
        self.city_dropdown = CustomDropdown(options=[])
        self.city_dropdown.bind(selected=self._on_city_selected)
        city_row.add_widget(self.city_dropdown)
        self._outdoor_rows.append(city_row)

        self._outdoor_rows.append(SpacerBox(size_hint_y=0.02))

        # Daylight hours (auto-calculated, display-only)
        daylight_row = ContentBox(orientation="horizontal")
        daylight_row.add_widget(FieldLabel(text=lang.LIGHT_SCHEDULE_LABEL, size_hint_x=0.3))
        self._daylight_label = FieldLabel(text="— h")
        daylight_row.add_widget(self._daylight_label)
        self._outdoor_rows.append(daylight_row)

    # ── Cascading dropdown callbacks ───────────────────────────────────────

    def _on_continent_selected(self, instance, value):
        countries = sorted(LOCATIONS.get(value, {}).keys())
        self.country_dropdown.options = countries
        if countries:
            self.country_dropdown.select_option(countries[0])
        else:
            self.country_dropdown.select_option("")
            self.city_dropdown.options = []
            self._daylight_label.text = "— h"

    def _on_country_selected(self, instance, value):
        continent = self.continent_dropdown.selected
        cities_data = LOCATIONS.get(continent, {}).get(value, [])
        city_names = [c["city"] for c in cities_data]
        self.city_dropdown.options = city_names
        if city_names:
            self.city_dropdown.select_option(city_names[0])
        else:
            self._daylight_label.text = "— h"

    def _on_city_selected(self, instance, value):
        city_data = self._get_selected_city_data()
        if city_data:
            hours = _daylight_hours(
                city_data["lat"], city_data["lon"], city_data["tz"],
            )
            self._daylight_label.text = f"{hours:.1f}h / {24 - hours:.1f}h"
        else:
            self._daylight_label.text = "— h"

    def _get_selected_city_data(self):
        """Return the dict for the currently selected city, or None."""
        continent = self.continent_dropdown.selected
        country = self.country_dropdown.selected
        city_name = self.city_dropdown.selected
        cities = LOCATIONS.get(continent, {}).get(country, [])
        for c in cities:
            if c["city"] == city_name:
                return c
        return None

    # ── Indoor / Outdoor toggle ────────────────────────────────────────────

    def _on_type_toggle(self, instance, state):
        if state != "down":
            return
        if instance is self.indoor_btn:
            self._show_indoor()
        else:
            self._show_outdoor()

    def _show_indoor(self):
        self._dynamic_box.clear_widgets()
        for w in self._indoor_rows:
            self._dynamic_box.add_widget(w)

    def _show_outdoor(self):
        self._dynamic_box.clear_widgets()
        for w in self._outdoor_rows:
            self._dynamic_box.add_widget(w)
        # Trigger initial cascade if continent is already selected
        if self.continent_dropdown.selected:
            self._on_continent_selected(None, self.continent_dropdown.selected)

    # ── /x live label ──────────────────────────────────────────────────────

    def _on_light_hours_text(self, instance, value):
        text = value.strip()
        if text.isdigit():
            on = min(int(text), 24)
            off = 24 - on
            self._light_off_label.text = f"/ {off}"
            # clamp input if > 24
            if int(text) > 24:
                instance.text = "24"
        else:
            self._light_off_label.text = "/ —"

    # ── Lifecycle ──────────────────────────────────────────────────────────

    def on_enter(self):
        super().on_enter()
        self.name_input.text = ""
        self.indoor_btn.state = "down"
        self.outdoor_btn.state = "normal"
        self.led_btn.state = "normal"
        self.hps_btn.state = "normal"
        self.cfl_btn.state = "normal"
        self.wattage_input.text = ""
        self.light_hours_input.text = ""
        self._light_off_label.text = "/ —"
        self._daylight_label.text = "— h"
        self._show_indoor()

    # ── Save ───────────────────────────────────────────────────────────────

    def _on_save(self, *args):
        name = self.name_input.text.strip()
        if not name:
            shake_and_flash(self.name_input)
            return

        garden_type = "indoor" if self.indoor_btn.state == "down" else "outdoor"

        if garden_type == "indoor":
            light_type = ""
            if self.led_btn.state == "down":
                light_type = "LED"
            elif self.hps_btn.state == "down":
                light_type = "HPS"
            elif self.cfl_btn.state == "down":
                light_type = "CFL"

            wattage = self.wattage_input.text.strip()
            hours_on = self.light_hours_input.text.strip()
            hours_off = str(24 - int(hours_on)) if hours_on.isdigit() else ""

            garden = {
                "id": str(uuid4()),
                "name": name,
                "type": garden_type,
                "light_type": light_type,
                "light_wattage": wattage,
                "light_schedule": [int(hours_on), int(hours_off)] if hours_on.isdigit() and hours_off.isdigit() else [],
                "location": {},
                "plants": [],
                "created_at": date.today().isoformat(),
            }
        else:
            # Outdoor garden
            city_data = self._get_selected_city_data()
            if not city_data:
                shake_and_flash(self.city_dropdown)
                return

            hours = _daylight_hours(city_data["lat"], city_data["lon"], city_data["tz"])
            hours_on = round(hours)
            hours_off = 24 - hours_on

            garden = {
                "id": str(uuid4()),
                "name": name,
                "type": garden_type,
                "light_type": "natural",
                "light_wattage": "",
                "light_schedule": [hours_on, hours_off],
                "location": {
                    "continent": self.continent_dropdown.selected,
                    "country": self.country_dropdown.selected,
                    "city": city_data["city"],
                    "lat": city_data["lat"],
                    "lon": city_data["lon"],
                    "tz": city_data["tz"],
                },
                "plants": [],
                "created_at": date.today().isoformat(),
            }

        if storage.save_garden(garden):
            LOG.info("Created garden '%s' (%s)", name, garden["id"])
            app = App.get_running_app()
            app.current_garden_id = garden["id"]
            app.screen.current = "garden_view"
        else:
            LOG.error("Failed to save garden")

    def _on_cancel(self, *args):
        app = App.get_running_app()
        if app.previous_screen:
            app.screen.current = app.previous_screen
        else:
            gardens = storage.load_gardens()
            if gardens:
                app.screen.current = "select_garden"
            else:
                app.screen.current = "garden_view"
