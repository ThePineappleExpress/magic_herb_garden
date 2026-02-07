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

from strain_trie import trie_search
from storage import save_plant, load_plants
from effects import shake_and_flash
from labels import FieldLabel, TitleLabel, WarningLabel, HintLabel, WarningTitleLabel
from kivy.metrics import dp
from boxes import WrapperBox, ContentBox, ItemBox, SpacerBox, RedBox, YellowBox, GreenBox, DarkBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import MedTextInput, LargeTextInput, DaysTextInput
from screens import BaseScreen

CATALOG_FILE = "bin/db/seed_catalog.json"

def load_catalog():
    path = os.path.join(os.path.dirname(__file__), CATALOG_FILE)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SEED_CATALOG = load_catalog()


class SowSeedScreen(BaseScreen):
    theme = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_validating = False
        self.current_prefix = ""
        self.current_suggestion = ""

        sow_seed_screen = WrapperBox(orientation="horizontal")
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
        title = TitleLabel(text = f"Say something about your [color={TitleLabel().hex_color}]seed[/color]")
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        sow_seed_screen.add_widget(spacer_left)

        #Input screen
        layout = WrapperBox(orientation="vertical")
        # top title bar
        spacer = WrapperBox(size_hint_y=0.5)
        layout.add_widget(spacer)



        # Inputs

        plant_name = ContentBox(orientation="horizontal")
        label_plant_name = FieldLabel(text="Seedbank: ", size_hint_x=0.3)
        plant_name.add_widget(label_plant_name)
        self.input_plant_name = MedTextInput(hint_text="Select a name for your plant")
        plant_name.add_widget(self.input_plant_name)
        layout.add_widget(plant_name)


        plant_strain = ContentBox(orientation="horizontal")
        label_plant_strain = FieldLabel(text="Strain: ", size_hint_x=0.3)
        plant_strain.add_widget(label_plant_strain)
        self.input_plant_strain = MedTextInput(hint_text="What's on the box?")
        plant_strain.add_widget(self.input_plant_strain)
        layout.add_widget(plant_strain)

        # dropdown for suggestions
        self.strain_dropdown = DropDown(auto_width=False, width=400)
        self.dropdown_open = False
        self.suggestion_index = -1
        self.input_plant_strain.bind(text=self.on_strain_text)
        # listen for keyboard
        Window.bind(on_key_down=self.on_key_down)

        plant_description = ContentBox(orientation="horizontal")
        # reserve vertical space so multi-line input is visible
        plant_description.size_hint_y = None
        plant_description.height = dp(140)
        label_plant_description = FieldLabel(text="Info: ", size_hint_x=0.3)
        plant_description.add_widget(label_plant_description)
        self.input_plant_description = LargeTextInput(hint_text="Say something about your plant", multiline=True)
        self.input_plant_description.size_hint_y = None
        self.input_plant_description.height = dp(120)
        plant_description.add_widget(self.input_plant_description)
        layout.add_widget(plant_description)


        plant_genes = ContentBox(orientation="horizontal")
        label_plant_genes = FieldLabel(text="Heritage: ", size_hint_x=0.3)
        plant_genes.add_widget(label_plant_genes)
        input_plant_genes = ItemBox(orientation="horizontal")
        self.sati_btn = ToggleButton(text="Sativa", group="genes")
        input_plant_genes.add_widget(self.sati_btn)
        self.indi_btn = ToggleButton(text="Indica", group="genes")
        input_plant_genes.add_widget(self.indi_btn)
        self.hybrid_btn = ToggleButton(text="Hybrid", group="genes")
        input_plant_genes.add_widget(self.hybrid_btn)
        plant_genes.add_widget(input_plant_genes)
        layout.add_widget(plant_genes)


        plant_type = ContentBox(orientation="horizontal")
        label_plant_type = FieldLabel(text="Type: ", size_hint_x=0.3)
        plant_type.add_widget(label_plant_type)
        input_plant_type = ItemBox(orientation="horizontal")
        self.auto_btn = ToggleButton(text="Automatic", group="type")
        input_plant_type.add_widget(self.auto_btn)
        self.photo_btn = ToggleButton(text="Photoperiodic", group="type")
        input_plant_type.add_widget(self.photo_btn)
        plant_type.add_widget(input_plant_type)
        layout.add_widget(plant_type)


        to_flower = ContentBox(orientation="horizontal")
        label_to_flower = FieldLabel(text="Flowering period: ", size_hint_x=0.3)
        to_flower.add_widget(label_to_flower)
        input_to_flower = ItemBox(orientation="horizontal")
        self.days_to_flower = DaysTextInput(hint_text="Days to flower")
        input_to_flower.add_widget(self.days_to_flower)
        to_flower.add_widget(input_to_flower)
        layout.add_widget(to_flower)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)


        # buttons
        buttons_wrapper = ContentBox(orientation="vertical")
        spacer = SpacerBox(size_hint_y=0.2)
        buttons_wrapper.add_widget(spacer)

        buttons_layout = ItemBox(orientation="vertical")
        buttons = ItemBox(orientation="horizontal")

        vert_spacer = WrapperBox()
        buttons.add_widget(vert_spacer)

        cancel_btn = ButtonRed(text="Cancel")
        cancel_btn.bind(on_press=self.on_cancel)
        buttons.add_widget(cancel_btn)

        save_btn = ButtonGreen(text="Next")
        save_btn.bind(on_press=self.next_screen)
        buttons.add_widget(save_btn)

        buttons_layout.add_widget(buttons)
        buttons_wrapper.add_widget(buttons_layout)
        layout.add_widget(buttons_wrapper)
        spacer = WrapperBox(size_hint_y=0.5)
        layout.add_widget(spacer)

        sow_seed_screen.add_widget(layout)

        spacer_right = SpacerBox(size_hint_x=0.1)
        sow_seed_screen.add_widget(spacer_right)

        # add everything to this Screen
        self.add_widget(sow_seed_screen)

    def clear_fields(self):
        # Text inputs
        self.input_plant_name.text = ""
        self.input_plant_strain.text = ""
        self.input_plant_description.text = ""
        self.days_to_flower.text = ""
        # Toggle buttons (genes)
        self.sati_btn.state = "normal"
        self.indi_btn.state = "normal"
        self.hybrid_btn.state = "normal"
        # Toggle buttons (type)
        self.auto_btn.state = "normal"
        self.photo_btn.state = "normal"


    def confirm_action(self):
        file = load_plants()
        app = App.get_running_app()
        self.clear_fields()
        if file == []:
            app.screen.current = "empty_garden"
        else:
            app.screen.current = "garden_view"
        return app.screen


    def next_screen(self, instance):
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
        app.pending_plant_data = {
            "name": self.input_plant_name.text.strip(),
            "strain": self.input_plant_strain.text.strip(),
            "notes": self.input_plant_description.text.strip(),
            "genes": (
                "Indica" if self.indi_btn.state == "down" else
                "Sativa" if self.sati_btn.state == "down" else
                "Hybrid" if self.hybrid_btn.state == "down" else ""
            ),
            "type": (
                "Automatic" if self.auto_btn.state == "down" else
                "Photoperiod" if self.photo_btn.state == "down" else ""
            ),
            "days_to_flower": self.days_to_flower.text.strip(),
        }
        app.screen.current = "set_environment"

    def on_cancel(self, instance):
        app = App.get_running_app()
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.confirm_callback = lambda *_: self.confirm_action()
        are_you_sure.prompt_text = "Are you sure you want to cancel and lose all unsaved changes?"
        app.previous_screen = app.screen.current
        app.screen.current = "are_you_sure"
    
    def on_strain_text(self, instance, value):
        self.current_prefix = value
        text = value.strip()

        # too short
        if len(text) < 1:
            self.current_suggestion = ""
            if self.dropdown_open:
                self.strain_dropdown.dismiss()
                self.dropdown_open = False
            self.suggestion_index = -1
            return

        # search
        try:
            matches = trie_search(text)
        except Exception as e:
            self.current_suggestion = ""
            if self.dropdown_open:
                self.strain_dropdown.dismiss()
                self.dropdown_open = False
            self.suggestion_index = -1
            return

        # no matches
        if not matches:
            self.current_suggestion = ""
            if self.dropdown_open:
                self.strain_dropdown.dismiss()
                self.dropdown_open = False
            self.suggestion_index = -1
            return

        # we have matches
        self.current_suggestion = matches[0]

        # rebuild dropdown *now*
        self.strain_dropdown.clear_widgets()
        self.suggestion_index = -1

        for name in matches:
            btn = Factory.SuggestionButton(text=name.title())
            btn.bind(on_release=self.on_strain_pick)
            self.strain_dropdown.add_widget(btn)

        if not self.dropdown_open:
            self.strain_dropdown.open(self.input_plant_strain)
            self.dropdown_open = True

        self._update_suggestion_highlight()

    def _get_suggestion_buttons(self):
        if not self.strain_dropdown.children:
            return []

        container = self.strain_dropdown.children[0]  
        btns = [w for w in container.children if isinstance(w, Button)]
        btns.sort(key=lambda b: b.y, reverse=True)
        return btns
    
    def validate(self):
        invalid = []
        # required text inputs
        if not self.input_plant_name.text.strip():
            invalid.append(self.input_plant_name)
        if not self.input_plant_strain.text.strip():
            invalid.append(self.input_plant_strain)

        # genes (one of the three must be down)
        if (self.sati_btn.state, self.indi_btn.state, self.hybrid_btn.state).count("down") == 0:
            invalid.extend([self.sati_btn, self.indi_btn, self.hybrid_btn])

        # type
        if (self.auto_btn.state, self.photo_btn.state).count("down") == 0:
            invalid.extend([self.auto_btn, self.photo_btn])

        # days_to_flower
        if not self.days_to_flower.text.strip():
            invalid.append(self.days_to_flower)

        return invalid

    def _end_validation(self, dt):
        self._is_validating = False

    def on_strain_pick(self, button):
        self.input_plant_strain.text = button.text
        self.current_suggestion = button.text
        self.input_plant_strain.cursor = (len(button.text), 0)
        self.strain_dropdown.dismiss()
        self.dropdown_open = False
        self.suggestion_index = -1
        self.input_plant_strain.hint_text = ""

        self._apply_catalog_for_strain(button.text)

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
        name = rec.get("breeder", "Unknown Breeder") if rec else "Unknown Breeder"
        genes = rec.get("genes", "")
        stype = rec.get("type", "")
        days_to_flower = rec.get("days_to_flower", "")
        self.input_plant_name.text = name
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