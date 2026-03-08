"""add_garden.py - New garden creation screen."""

import logging
from datetime import date
from uuid import uuid4

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.togglebutton import ToggleButton

from boxes import ContentBox, ItemBox, SpacerBox, WrapperBox
from buttons import ButtonGreen, ButtonRed
from effects import shake_and_flash
from labels import FieldLabel, TitleLabel
from screens import BaseScreen
from text_inputs import MedTextInput
from ui_builders import create_initial_layout
import lang
import storage

LOG = logging.getLogger(__name__)


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
        type_box.add_widget(self.indoor_btn)
        type_box.add_widget(self.outdoor_btn)
        type_row.add_widget(type_box)
        layout.add_widget(type_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # Light type (Indoor only)
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
        layout.add_widget(light_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # Light wattage
        watt_row = ContentBox(orientation="horizontal")
        watt_row.add_widget(FieldLabel(text=lang.LIGHT_WATTAGE_LABEL, size_hint_x=0.3))
        self.wattage_input = MedTextInput(hint_text=lang.HINT_LIGHT_WATTAGE, input_filter="int")
        watt_row.add_widget(self.wattage_input)
        layout.add_widget(watt_row)

        layout.add_widget(SpacerBox(size_hint_y=0.02))

        # Light schedule
        sched_row = ContentBox(orientation="horizontal")
        sched_row.add_widget(FieldLabel(text=lang.LIGHT_SCHEDULE_LABEL, size_hint_x=0.3))
        self.light_hours_input = MedTextInput(hint_text=lang.HINT_LIGHT_HOURS, input_filter="int")
        sched_row.add_widget(self.light_hours_input)
        layout.add_widget(sched_row)

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

    def on_enter(self):
        self.name_input.text = ""
        self.indoor_btn.state = "down"
        self.outdoor_btn.state = "normal"
        self.led_btn.state = "normal"
        self.hps_btn.state = "normal"
        self.cfl_btn.state = "normal"
        self.wattage_input.text = ""
        self.light_hours_input.text = ""

    def _on_save(self, *args):
        name = self.name_input.text.strip()
        if not name:
            shake_and_flash(self.name_input)
            return

        garden_type = "indoor" if self.indoor_btn.state == "down" else "outdoor"
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
            "location": "",
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
