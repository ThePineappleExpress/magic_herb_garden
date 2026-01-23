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
from storage import save_plant
from effects import shake_and_flash
from labels import FieldLabel, TitleLabel, WarningLabel, HintLabel, WarningTitleLabel
from boxes import WrapperBox, ContentBox, ItemBox, SpacerBox, RedBox, YellowBox, GreenBox, DarkBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import MedTextInput, LargeTextInput, NumTextInput

CATALOG_FILE = "bin/db/seed_catalog.json"

def load_catalog():
    path = os.path.join(os.path.dirname(__file__), CATALOG_FILE)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SEED_CATALOG = load_catalog()


class SowSeedScreen(Screen):
    theme = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_validating = False
        self.current_prefix = ""
        self.current_suggestion = ""

        data_input = WrapperBox(orientation="horizontal")
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
        data_input.add_widget(spacer_left)

        #Input screen
        layout = WrapperBox(orientation="vertical")
        # top title bar
        spacer = WrapperBox(size_hint_y=0.5)
        layout.add_widget(spacer)



        # Inputs

        plant_name = ContentBox(orientation="horizontal")
        label_plant_name = FieldLabel(text="Name: ", size_hint_x=0.3)
        plant_name.add_widget(label_plant_name)
        self.input_plant_name = MedTextInput(hint_text="Select a name for your plant", multiline=False)
        plant_name.add_widget(self.input_plant_name)
        layout.add_widget(plant_name)


        plant_strain = ContentBox(orientation="horizontal")
        label_plant_strain = FieldLabel(text="Strain: ", size_hint_x=0.3)
        plant_strain.add_widget(label_plant_strain)
        self.input_plant_strain = MedTextInput(hint_text="What's on the box?", multiline=False)
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
        label_plant_description = FieldLabel(text="Info: ", size_hint_x=0.3)
        plant_description.add_widget(label_plant_description)
        self.input_plant_description = LargeTextInput(hint_text="Say something about your plant", multiline=True)
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
        self.days_to_flower = NumTextInput(hint_text="Days to flower", input_filter="int", multiline=False)
        input_to_flower.add_widget(self.days_to_flower)
        to_flower.add_widget(input_to_flower)
        layout.add_widget(to_flower)

        pot_size = ContentBox(orientation="horizontal")
        label_pot_size = FieldLabel(text="Pot size: ", size_hint_x=0.3)
        pot_size.add_widget(label_pot_size)
        input_pot_size = ItemBox(orientation="horizontal")
        self.pot_slider = Slider(min=1, max=30, step=1, value=9)
        self.pot_slider.bind(value=self.on_pot_change)
        input_pot_size.add_widget(self.pot_slider)
        self.pot_label = HintLabel(text="9L", size_hint_x=0.3, halign="left")
        input_pot_size.add_widget(self.pot_label)
        pot_size.add_widget(input_pot_size)
        layout.add_widget(pot_size)


        warning_layout = ContentBox(orientation="horizontal", size_hint_y=2.5)
        warning_spacer = SpacerBox(size_hint_x=0.3)
        warning_layout.add_widget(warning_spacer)
        warning_box = DarkBox(orientation="vertical")
        warning_title = WarningTitleLabel(text="Watering and feeding:", halign="left", size_hint_y=0.35)
        warning_box.add_widget(warning_title)
        warning_label = WarningLabel(text="Consult the packaging or the breeder for estimated profiles.\nValues will adjust automatically during your plants life.\nIf you are not sure just leave both sliders in the default position.")
        warning_box.add_widget(warning_label)
        warning_layout.add_widget(warning_box)
        layout.add_widget(warning_layout)


        plant_thirst = ContentBox(orientation="horizontal")
        label_plant_thirst = FieldLabel(text="Watering: ", size_hint_x=0.3)
        plant_thirst.add_widget(label_plant_thirst)
        input_plant_thirst = DarkBox(orientation="horizontal")
        self.thirsty_slider = Slider(min=1, max=3, step=1, value=2)
        self.thirsty_label = HintLabel(text="Every 3 days", size_hint_x=0.3, halign="left", valign="middle")
        self.thirsty_slider.bind(value=self.on_thirst_change)
        input_plant_thirst.add_widget(self.thirsty_slider)
        input_plant_thirst.add_widget(self.thirsty_label)
        plant_thirst.add_widget(input_plant_thirst)
        layout.add_widget(plant_thirst)


        plant_hunger = ContentBox(orientation="horizontal")
        label_plant_hunger = FieldLabel(text="Feeding: ", size_hint_x=0.3)
        plant_hunger.add_widget(label_plant_hunger)
        input_plant_hunger = DarkBox(orientation="horizontal")
        self.hunger_slider = Slider(min=1, max=3, step=1, value=2)
        self.hunger_slider.bind(value=self.on_hunger_change)
        input_plant_hunger.add_widget(self.hunger_slider)
        self.hunger_label = HintLabel(text="Every 2nd Watering", size_hint_x=0.3, halign="left", valign="middle")
        input_plant_hunger.add_widget(self.hunger_label)
        plant_hunger.add_widget(input_plant_hunger)
        layout.add_widget(plant_hunger)


        medium_type = ContentBox(orientation="horizontal")
        label_medium_type = FieldLabel(text="Medium: ", size_hint_x=0.3)
        medium_type.add_widget(label_medium_type)
        input_medium_type = ItemBox(orientation="horizontal")
        self.type_soil = ToggleButton(text="Soil", group="medium_type")
        self.type_coco = ToggleButton(text="Coco", group="medium_type")
        self.type_mineral = ToggleButton(text="Mineral", group="medium_type")
        self.type_hydro = ToggleButton(text="Hydro", group="medium_type")
        input_medium_type.add_widget(self.type_soil)
        input_medium_type.add_widget(self.type_coco)
        input_medium_type.add_widget(self.type_mineral)
        input_medium_type.add_widget(self.type_hydro)
        medium_type.add_widget(input_medium_type)
        layout.add_widget(medium_type)
        

        medium_nutrients = ContentBox(orientation="horizontal")
        label_medium_nutrients = FieldLabel(text="Fertilized: ", size_hint_x=0.3)
        medium_nutrients.add_widget(label_medium_nutrients)
        input_medium_nutrients = ItemBox(orientation="horizontal")
        self.fert_btn = ToggleButton(text="Fertilized", group="medium_nutrients")
        self.unfert_btn = ToggleButton(text="Bare", group="medium_nutrients")
        input_medium_nutrients.add_widget(self.fert_btn)
        input_medium_nutrients.add_widget(self.unfert_btn)
        medium_nutrients.add_widget(input_medium_nutrients)
        layout.add_widget(medium_nutrients)


        fertilizer_type = ContentBox(orientation="horizontal")
        label_fertilizer_type = FieldLabel(text="Your fertilizer: ", size_hint_x=0.3)
        fertilizer_type.add_widget(label_fertilizer_type)
        input_fertilizer_type = ItemBox(orientation="horizontal")
        self.org_btn = ToggleButton(text="Organic", group="fertilizer_type")
        input_fertilizer_type.add_widget(self.org_btn)
        self.min_btn = ToggleButton(text="Mineral", group="fertilizer_type")
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

        save_btn = ButtonGreen(text="Save")
        save_btn.bind(on_press=self.on_save_plant)
        buttons.add_widget(save_btn)

        cancel_btn = ButtonRed(text="Cancel")
        cancel_btn.bind(on_press=App.get_running_app().go_back)
        buttons.add_widget(cancel_btn)

        buttons_layout.add_widget(buttons)
        buttons_wrapper.add_widget(buttons_layout)
        layout.add_widget(buttons_wrapper)
        spacer = WrapperBox(size_hint_y=0.5)
        layout.add_widget(spacer)

        data_input.add_widget(layout)

        spacer_right = SpacerBox(size_hint_x=0.1)
        data_input.add_widget(spacer_right)

        # add everything to this Screen
        self.add_widget(data_input)


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
            btn = Factory.SuggestionButton(text=name)
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

        # medium
        if all(btn.state == "normal" for btn in (self.type_soil, self.type_coco, self.type_mineral, self.type_hydro)):
            invalid.extend([self.type_soil, self.type_coco, self.type_mineral, self.type_hydro])

        # medium nutrients
        if (self.fert_btn.state, self.unfert_btn.state).count("down") == 0:
            invalid.extend([self.fert_btn, self.unfert_btn])

        # fertilizer type
        if (self.org_btn.state, self.min_btn.state).count("down") == 0:
            invalid.extend([self.org_btn, self.min_btn])

        # days_to_flower
        if not self.days_to_flower.text.strip():
            invalid.append(self.days_to_flower)

        return invalid
    
    def save_genes(self):
        if self.indi_btn.state == "down":
            return "Indica"
        if self.sati_btn.state == "down":
            return "Sativa"
        if self.hybrid_btn.state == "down":
            return "Hybrid"
        
    def save_type(self):
        if self.auto_btn.state == "down":
            return "Automatic"
        if self.photo_btn.state == "down":
            return "Photoperiodic"
        
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
    
    def on_strain_pick(self, button):
        self.input_plant_strain.text = button.text
        self.current_suggestion = button.text
        self.input_plant_strain.cursor = (len(button.text), 0)
        self.strain_dropdown.dismiss()
        self.dropdown_open = False
        self.suggestion_index = -1
        self.input_plant_strain.hint_text = ""

        self._apply_catalog_for_strain(button.text)

    def on_pot_change(self, slider, value):
        self.pot_label.text = f"{int(value)}L"

    def on_thirst_change(self, slider, value):
        display = 5 - int(value)
        self.thirsty_label.text = f"Every {display} days"

    def on_hunger_change(self, slider, value):
        display = 4 - int(value)
        if display == 1:
            self.hunger_label.text = f"Every watering"
        elif display == 2:
            self.hunger_label.text = f"Every 2nd watering"
        else:
            self.hunger_label.text = f"Every 3rd watering"

    def on_save_plant(self, instance):
        # if we’re already shaking things, ignore extra clicks
        if self._is_validating:
            return

        invalid = self.validate()  # you already have something like this, or add it

        if invalid:
            self._is_validating = True
            for w in set(invalid):
                # decide which channel to flash
                use_bg = isinstance(w, (ButtonGreen, ButtonRed))
                use_text = isinstance(w, (MedTextInput, LargeTextInput))

                shake_and_flash(w, use_bg=use_bg, use_text=use_text)

            # schedule flag reset after animations are done
            from kivy.clock import Clock
            Clock.schedule_once(self._end_validation, 0.5)  # adjust to match your anim duration
            return

        # only reach here if all fields are valid
        plant = {
            "id": str(uuid.uuid4()),
            "name": self.input_plant_name.text.strip(),
            "strain": self.input_plant_strain.text.strip(),
            "notes": self.input_plant_description.text.strip(),
            "genes": self.save_genes(),
            "type": self.save_type(),
            "days_to_flower": int(self.days_to_flower.text),
            "pot_size_l": int(self.pot_slider.value),
            "watering_profile": int(self.thirsty_slider.value),
            "feeding_profile": int(self.hunger_slider.value),
            "medium": self.save_medium_type(),
            "medium_nutrients": self.save_medium_nutrients(),
            "fertilizer_type": self.save_fertilizer_type(),
            "date_planted": date.today().isoformat(),
        }
        save_plant(plant)
        app = App.get_running_app()
        garden = app.screen.get_screen("garden_view")
        garden.refresh_plants()
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
