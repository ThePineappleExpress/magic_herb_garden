import json
import os
import uuid
from datetime import date
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window

from storage import add_plant_to_garden
from effects import shake_and_flash
import lang
from labels import FieldLabel, TitleLabel, WarningLabel, HintLabel, WarningTitleLabel
from boxes import WrapperBox, ContentBox, ItemBox, SpacerBox, RedBox, YellowBox, GreenBox, DarkBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import MedTextInput, LargeTextInput, NumTextInput
from screens import BaseScreen

CATALOG_FILE = "bin/db/seed_catalog.json"

def load_catalog():
    path = os.path.join(os.path.dirname(__file__), CATALOG_FILE)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SEED_CATALOG = load_catalog()


class SetEnvironmentScreen(BaseScreen):
    theme = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_validating = False
        self.current_prefix = ""
        self.current_suggestion = ""

        set_environment_screen = WrapperBox(orientation="horizontal")
        spacer_left = SpacerBox(size_hint_x=0.1)
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
        title = TitleLabel(text=lang.SCREEN_TITLE_ENV.format(color=TitleLabel().hex_color))
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        set_environment_screen.add_widget(spacer_left)

        #Input screen
        layout = WrapperBox(orientation="vertical")
        # top title bar
        spacer = WrapperBox(size_hint_y=0.5)
        layout.add_widget(spacer)



        # Inputs

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        warning_layout = ContentBox(orientation="horizontal", size_hint_y=2.5)
        warning_spacer = SpacerBox(size_hint_x=0.3)
        warning_layout.add_widget(warning_spacer)
        warning_box = DarkBox(orientation="vertical")
        warning_title = WarningTitleLabel(text=lang.SET_ENV_WARNING_TITLE, halign="left")
        warning_box.add_widget(warning_title)
        warning_label = WarningLabel(text=lang.SET_ENV_WARNING_BODY)
        warning_box.add_widget(warning_label)
        warning_layout.add_widget(warning_box)
        layout.add_widget(warning_layout)


        plant_thirst = ContentBox(orientation="horizontal")
        label_plant_thirst = FieldLabel(text=lang.WATERING_LABEL, size_hint_x=0.3)
        plant_thirst.add_widget(label_plant_thirst)
        input_plant_thirst = DarkBox(orientation="horizontal")
        self.thirsty_slider = Slider(min=1, max=3, step=1, value=2)
        self.thirsty_label = HintLabel(text=lang.EVERY_3_DAYS, size_hint_x=0.3, halign="left", valign="middle")
        self.thirsty_slider.bind(value=self.on_thirst_change)
        input_plant_thirst.add_widget(self.thirsty_slider)
        input_plant_thirst.add_widget(self.thirsty_label)
        plant_thirst.add_widget(input_plant_thirst)
        layout.add_widget(plant_thirst)


        plant_hunger = ContentBox(orientation="horizontal")
        label_plant_hunger = FieldLabel(text=lang.FEEDING_LABEL, size_hint_x=0.3)
        plant_hunger.add_widget(label_plant_hunger)
        input_plant_hunger = DarkBox(orientation="horizontal")
        self.hunger_slider = Slider(min=1, max=3, step=1, value=2)
        self.hunger_slider.bind(value=self.on_hunger_change)
        input_plant_hunger.add_widget(self.hunger_slider)
        self.hunger_label = HintLabel(text=lang.EVERY_2ND_WATERING, size_hint_x=0.3, halign="left", valign="middle")
        input_plant_hunger.add_widget(self.hunger_label)
        plant_hunger.add_widget(input_plant_hunger)
        layout.add_widget(plant_hunger)

        pot_size = ContentBox(orientation="horizontal")
        label_pot_size = FieldLabel(text=lang.POT_SIZE_LABEL, size_hint_x=0.3)
        pot_size.add_widget(label_pot_size)
        input_pot_size = ItemBox(orientation="horizontal")
        self.pot_slider = Slider(min=1, max=30, step=1, value=9)
        self.pot_slider.bind(value=self.on_pot_change)
        input_pot_size.add_widget(self.pot_slider)
        self.pot_label = HintLabel(text=lang.POT_LABEL_DEFAULT, valign="middle", halign="left", size_hint_x=0.3)
        input_pot_size.add_widget(self.pot_label)
        pot_size.add_widget(input_pot_size)
        layout.add_widget(pot_size)

        medium_type = ContentBox(orientation="horizontal")
        label_medium_type = FieldLabel(text=lang.MEDIUM_LABEL, size_hint_x=0.3)
        medium_type.add_widget(label_medium_type)
        input_medium_type = ItemBox(orientation="horizontal")
        self.type_soil = ToggleButton(text=lang.MEDIUM_SOIL, group="medium_type")
        self.type_coco = ToggleButton(text=lang.MEDIUM_COCO, group="medium_type")
        self.type_mineral = ToggleButton(text=lang.MEDIUM_MINERAL, group="medium_type")
        self.type_hydro = ToggleButton(text=lang.MEDIUM_HYDRO, group="medium_type")
        input_medium_type.add_widget(self.type_soil)
        input_medium_type.add_widget(self.type_coco)
        input_medium_type.add_widget(self.type_mineral)
        input_medium_type.add_widget(self.type_hydro)
        medium_type.add_widget(input_medium_type)
        layout.add_widget(medium_type)
        

        medium_nutrients = ContentBox(orientation="horizontal")
        label_medium_nutrients = FieldLabel(text=lang.FERTILIZED_LABEL, size_hint_x=0.3)
        medium_nutrients.add_widget(label_medium_nutrients)
        input_medium_nutrients = ItemBox(orientation="horizontal")
        self.fert_btn = ToggleButton(text=lang.FERTILIZED, group="medium_nutrients")
        self.unfert_btn = ToggleButton(text=lang.BARE, group="medium_nutrients")
        input_medium_nutrients.add_widget(self.fert_btn)
        input_medium_nutrients.add_widget(self.unfert_btn)
        medium_nutrients.add_widget(input_medium_nutrients)
        layout.add_widget(medium_nutrients)


        fertilizer_type = ContentBox(orientation="horizontal")
        label_fertilizer_type = FieldLabel(text=lang.YOUR_FERTILIZER_LABEL, size_hint_x=0.3)
        fertilizer_type.add_widget(label_fertilizer_type)
        input_fertilizer_type = ItemBox(orientation="horizontal")
        self.org_btn = ToggleButton(text=lang.FERTILIZER_ORGANIC, group="fertilizer_type")
        input_fertilizer_type.add_widget(self.org_btn)
        self.min_btn = ToggleButton(text=lang.FERTILIZER_MINERAL, group="fertilizer_type")
        input_fertilizer_type.add_widget(self.min_btn)
        fertilizer_type.add_widget(input_fertilizer_type)
        layout.add_widget(fertilizer_type)

        # buttons
        buttons_wrapper = ContentBox(orientation="vertical")
        spacer = SpacerBox(size_hint_y=0.2)
        buttons_wrapper.add_widget(spacer)

        buttons_layout = ItemBox(orientation="vertical")
        buttons = ItemBox(orientation="horizontal")

        vert_spacer = WrapperBox()
        buttons.add_widget(vert_spacer)

        cancel_btn = ButtonRed(text=lang.BUTTON_CANCEL)
        cancel_btn.bind(on_press=self.on_back_pressed)
        buttons.add_widget(cancel_btn)

        save_btn = ButtonGreen(text=lang.BUTTON_SAVE)
        save_btn.bind(on_press=self.on_save_plant)
        buttons.add_widget(save_btn)

        buttons_layout.add_widget(buttons)
        buttons_wrapper.add_widget(buttons_layout)
        layout.add_widget(buttons_wrapper)
        spacer = WrapperBox(size_hint_y=0.5)
        layout.add_widget(spacer)

        set_environment_screen.add_widget(layout)

        spacer_right = SpacerBox(size_hint_x=0.1)
        set_environment_screen.add_widget(spacer_right)

        # add everything to this Screen
        self.add_widget(set_environment_screen)

    def clear_fields(self):

        # Sliders
        self.thirsty_slider.value = 2
        self.hunger_slider.value = 2
        self.pot_slider.value = 9
        # Medium type
        self.type_soil.state = "normal"
        self.type_coco.state = "normal"
        self.type_mineral.state = "normal"
        self.type_hydro.state = "normal"
        # Medium nutrients
        self.fert_btn.state = "normal"
        self.unfert_btn.state = "normal"
        # Fertilizer type
        self.org_btn.state = "normal"
        self.min_btn.state = "normal"
        # Reset labels if needed
        self.thirsty_label.text = lang.EVERY_3_DAYS
        self.hunger_label.text = lang.EVERY_2ND_WATERING
        self.pot_label.text = lang.POT_LABEL_DEFAULT

    def confirm_action(self):
        app = App.get_running_app()
        self.clear_fields()
        app.screen.current = "garden_view"
        return app.screen

    def on_back_pressed(self, instance):
        app = App.get_running_app()
        app.screen.current = "sow_seed"
    
    
    def validate(self):
        invalid = []

        # medium
        if all(btn.state == "normal" for btn in (self.type_soil, self.type_coco, self.type_mineral, self.type_hydro)):
            invalid.extend([self.type_soil, self.type_coco, self.type_mineral, self.type_hydro])

        # medium nutrients
        if (self.fert_btn.state, self.unfert_btn.state).count("down") == 0:
            invalid.extend([self.fert_btn, self.unfert_btn])

        # fertilizer type
        if (self.org_btn.state, self.min_btn.state).count("down") == 0:
            invalid.extend([self.org_btn, self.min_btn])

        return invalid
    
        
    def save_medium_type(self):
        if self.type_soil.state == "down":
            return "soil"
        if self.type_coco.state == "down":
            return "coco"
        if self.type_mineral.state == "down":
            return "rockwool"
        if self.type_hydro.state == "down":
            return "hydro"
        
    def save_medium_nutrients(self):
        if self.fert_btn.state == "down":
            return "fertilized"
        if self.unfert_btn.state == "down":
            return "bare"
        
    def save_fertilizer_type(self):
        if self.org_btn.state == "down":
            return "organic"
        if self.min_btn.state == "down":
            return "mineral"
    
    def on_pot_change(self, slider, value):
        self.pot_label.text = lang.POT_SIZE_FMT.format(n=int(value))

    def on_thirst_change(self, slider, value):
        display = 5 - int(value)
        self.thirsty_label.text = lang.EVERY_N_DAYS.format(n=display)

    def on_hunger_change(self, slider, value):
        display = 4 - int(value)
        if display == 1:
            self.hunger_label.text = lang.EVERY_WATERING
        elif display == 2:
            self.hunger_label.text = lang.EVERY_2ND_WATERING
        else:
            self.hunger_label.text = lang.EVERY_3RD_WATERING

    def on_save_plant(self, instance):
        # if we’re already shaking things, ignore extra clicks
        if self._is_validating:
            return

        invalid = self.validate()

        if invalid:
            self._is_validating = True
            for w in set(invalid):
                # decide which channel to flash
                use_bg = isinstance(w, (ButtonGreen, ButtonRed))
                use_text = isinstance(w, (MedTextInput, LargeTextInput))
                shake_and_flash(w, use_bg=use_bg, use_text=use_text)

            # schedule flag reset after animations are done
            from kivy.clock import Clock
            Clock.schedule_once(self._end_validation, 0.5)
            return

        app = App.get_running_app()
        pending = getattr(app, "pending_plant_data", {})
        # only reach here if all fields are valid
        plant = {
            "id": str(uuid.uuid4()),
            "name": str(pending.get("name", "")),
            "strain": str(pending.get("strain", "")),
            "notes": str(pending.get("notes", "")),
            "genes": str(pending.get("genes", "")),
            "type": str(pending.get("type", "")),
            "days_to_flower": int(pending.get("days_to_flower")),
            "pot_size_l": int(self.pot_slider.value),
            "watering_profile": int(self.thirsty_slider.value),
            "feeding_profile": int(self.hunger_slider.value),
            "medium": str(self.save_medium_type()),
            "medium_nutrients": str(self.save_medium_nutrients()),
            "fertilizer_type": str(self.save_fertilizer_type()),
            "date_planted": date.today().isoformat(),
        }
        garden_id = getattr(app, 'current_garden_id', None)
        if garden_id:
            add_plant_to_garden(garden_id, plant)
        self.clear_fields()
        app.pending_plant_data = {}
        garden_screen = app.screen.get_screen("garden_view")
        garden_screen.refresh_plants()
        app.screen.current = "garden_view"

    def _end_validation(self, dt):
        self._is_validating = False

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if not self.input_plant_strain.focus:
            return False

        TAB = 9
        ENTER = 13
        RIGHT = 275
        UP = 273
        DOWN = 274
        ESC = 27

        # ESC: close dropdown and clear selection
        if key == ESC and self.dropdown_open:
            self.strain_dropdown.dismiss()
            self.dropdown_open = False
            self.suggestion_index = -1
            return True

        # Arrow navigation only if dropdown is open
        if self.dropdown_open and key in (UP, DOWN):
            btns = self._get_suggestion_buttons()
            if not btns:
                return False

            if self.suggestion_index == -1:
                self.suggestion_index = 0 if key == DOWN else len(btns) - 1
            else:
                if key == DOWN:
                    self.suggestion_index = (self.suggestion_index + 1) % len(btns)
                else:
                    self.suggestion_index = (self.suggestion_index - 1) % len(btns)

            self._update_suggestion_highlight()
            return True

        # Enter/Tab/Right: if dropdown open and something selected, pick it and STOP
        if key in (TAB, ENTER, RIGHT) and self.dropdown_open and self.suggestion_index != -1:
            btns = self._get_suggestion_buttons()
            if 0 <= self.suggestion_index < len(btns):
                self.on_strain_pick(btns[self.suggestion_index])
                return True

        # Inline completion: only when dropdown is CLOSED
        if key in (TAB, ENTER, RIGHT) and self.current_suggestion and not self.dropdown_open:
            self.input_plant_strain.text = self.current_suggestion
            self.input_plant_strain.cursor = (len(self.current_suggestion), 0)
            self.input_plant_strain.hint_text = ""
            self._apply_catalog_for_strain(self.current_suggestion)
            return True

        return False
        
    def _update_suggestion_highlight(self):
        btns = self._get_suggestion_buttons()
        for i, btn in enumerate(btns):
            if i == self.suggestion_index:
                btn.background_color = App.get_running_app().theme.nice_yellow
                btn.color = App.get_running_app().theme.dark_gray
            else:
                btn.background_color = App.get_running_app().theme.nice_green
                btn.color = App.get_running_app().theme.off_white
    
    def _apply_catalog_for_strain(self, strain_name):
        raw = strain_name.strip()
        lower = raw.lower()

        # case-insensitive exact match
        rec = next(
            (r for r in SEED_CATALOG
            if r.get("strain", "").strip().lower() == lower),
            None
        )

        genes = rec.get("genes", "")
        stype = rec.get("type", "")
        days_to_flower = rec.get("days_to_flower", "")
        # reset gene buttons
        for btn in (self.sati_btn, self.indi_btn, self.hybrid_btn):
            btn.state = "normal"

        if genes == "Indica":
            self.indi_btn.state = "down"
        elif genes == "Sativa":
            self.sati_btn.state = "down"
        elif genes == "Hybrid":
            self.hybrid_btn.state = "down"

        # reset type buttons
        for btn in (self.auto_btn, self.photo_btn):
            btn.state = "normal"

        if stype == "Automatic":
            self.auto_btn.state = "down"
        elif stype == "Photoperiod":
            self.photo_btn.state = "down"

        self.days_to_flower.text = days_to_flower