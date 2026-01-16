
import uuid
from datetime import date
from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder

from storage import save_plant
from effects import shake_and_flash
from helpers import rgba_to_hex

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
    hint_color = ListProperty([0.259, 0.416, 0.353, 1 ]) # empty = “no override”
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

class SowSeedScreen(Screen):
    theme = ObjectProperty(None)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._is_validating = False

        data_input = WrapperBox(orientation="horizontal")
        spacer_left = SpacerBox(size_hint_x=0.2)
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
        spacer = WrapperBox()
        layout.add_widget(spacer)

        window_title = ContentBox(orientation="horizontal")
        layout.add_widget(window_title)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        # Inputs

        plant_name = ContentBox(orientation="horizontal")
        label_plant_name = FieldLabel(text="Name: ")
        plant_name.add_widget(label_plant_name)
        self.input_plant_name = MedTextInput(hint_text="Select a name for your plant", multiline=False)
        plant_name.add_widget(self.input_plant_name)
        layout.add_widget(plant_name)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        plant_strain = ContentBox(orientation="horizontal")
        label_plant_strain = FieldLabel(text="Strain: ")
        plant_strain.add_widget(label_plant_strain)
        self.input_plant_strain = MedTextInput(hint_text="What's on the box?", multiline=False)
        plant_strain.add_widget(self.input_plant_strain)
        layout.add_widget(plant_strain)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        plant_description = ContentBox(orientation="horizontal")
        label_plant_description = FieldLabel(text="Info: ")
        plant_description.add_widget(label_plant_description)
        self.input_plant_description = LargeTextInput(hint_text="Say something about your plant", multiline=True)
        plant_description.add_widget(self.input_plant_description)
        layout.add_widget(plant_description)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        plant_genes = ContentBox(orientation="horizontal")
        label_plant_genes = FieldLabel(text="Heritage: ")
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

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        plant_type = ContentBox(orientation="horizontal")
        label_plant_type = FieldLabel(text="Type: ")
        plant_type.add_widget(label_plant_type)
        input_plant_type = ItemBox(orientation="horizontal")
        self.auto_btn = ToggleButton(text="Automatic", group="type")
        input_plant_type.add_widget(self.auto_btn)
        self.photo_btn = ToggleButton(text="Photoperiodic", group="type")
        input_plant_type.add_widget(self.photo_btn)
        plant_type.add_widget(input_plant_type)
        layout.add_widget(plant_type)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        to_flower = ContentBox(orientation="horizontal")
        label_to_flower = FieldLabel(text="Flowering period: ")
        to_flower.add_widget(label_to_flower)
        input_to_flower = ItemBox(orientation="horizontal")
        self.days_to_flower = NumTextInput(hint_text="Days to flower", input_filter="int", multiline=False)
        input_to_flower.add_widget(self.days_to_flower)
        to_flower.add_widget(input_to_flower)
        layout.add_widget(to_flower)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        pot_size = ContentBox(orientation="horizontal")
        label_pot_size = FieldLabel(text="Pot size: ")
        pot_size.add_widget(label_pot_size)
        input_pot_size = ItemBox(orientation="horizontal")
        self.pot_slider = Slider(min=1, max=30, step=1, value=9)
        self.pot_slider.bind(value=self.on_pot_change)
        input_pot_size.add_widget(self.pot_slider)
        self.pot_label = HintLabel(text="9", size_hint_x=0.15)
        input_pot_size.add_widget(self.pot_label)
        pot_size.add_widget(input_pot_size)
        layout.add_widget(pot_size)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        plant_thirst = ContentBox(orientation="horizontal")
        label_plant_thirst = FieldLabel(text="Watering: ")
        plant_thirst.add_widget(label_plant_thirst)
        input_plant_thirst = ItemBox(orientation="horizontal")
        self.thirsty_slider = Slider(min=1, max=3, step=1, value=2)
        self.thirsty_label = HintLabel(text="2", size_hint_x=0.15)
        self.thirsty_slider.bind(value=self.on_thirst_change)
        input_plant_thirst.add_widget(self.thirsty_slider)
        input_plant_thirst.add_widget(self.thirsty_label)
        plant_thirst.add_widget(input_plant_thirst)
        layout.add_widget(plant_thirst)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        plant_hunger = ContentBox(orientation="horizontal")
        label_plant_hunger = FieldLabel(text="Feeding: ")
        plant_hunger.add_widget(label_plant_hunger)
        input_plant_hunger = ItemBox(orientation="horizontal")
        self.hunger_slider = Slider(min=1, max=3, step=1, value=2)
        self.hunger_slider.bind(value=self.on_hunger_change)
        input_plant_hunger.add_widget(self.hunger_slider)
        self.hunger_label = HintLabel(text="2", size_hint_x=0.15)
        input_plant_hunger.add_widget(self.hunger_label)
        plant_hunger.add_widget(input_plant_hunger)
        layout.add_widget(plant_hunger)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        medium_type = ContentBox(orientation="horizontal")
        label_medium_type = FieldLabel(text="Medium: ")
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

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        medium_nutrients = ContentBox(orientation="horizontal")
        label_medium_nutrients = FieldLabel(text="Fertilized: ")
        medium_nutrients.add_widget(label_medium_nutrients)
        input_medium_nutrients = ItemBox(orientation="horizontal")
        self.fert_btn = ToggleButton(text="Fertilized", group="medium_nutrients")
        self.unfert_btn = ToggleButton(text="Bare", group="medium_nutrients")
        input_medium_nutrients.add_widget(self.fert_btn)
        input_medium_nutrients.add_widget(self.unfert_btn)
        medium_nutrients.add_widget(input_medium_nutrients)
        layout.add_widget(medium_nutrients)

        spacer = SpacerBox(size_hint_y=0.02)
        layout.add_widget(spacer)

        fertilizer_type = ContentBox(orientation="horizontal")
        label_fertilizer_type = FieldLabel(text="Your fertilizer: ")
        fertilizer_type.add_widget(label_fertilizer_type)
        input_fertilizer_type = ItemBox(orientation="horizontal")
        self.org_btn = ToggleButton(text="Organic", group="fertilizer_type")
        input_fertilizer_type.add_widget(self.org_btn)
        self.min_btn = ToggleButton(text="Mineral", group="fertilizer_type")
        input_fertilizer_type.add_widget(self.min_btn)
        fertilizer_type.add_widget(input_fertilizer_type)
        layout.add_widget(fertilizer_type)

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

        save_btn = ButtonGreen(text="Save")
        save_btn.bind(on_press=self.on_save_plant)
        buttons.add_widget(save_btn)

        cancel_btn = ButtonRed(text="Cancel")
        cancel_btn.bind(on_press=App.get_running_app().go_back)
        buttons.add_widget(cancel_btn)

        buttons_layout.add_widget(buttons)
        buttons_wrapper.add_widget(buttons_layout)
        layout.add_widget(buttons_wrapper)

        spacer = WrapperBox(size_hint_y=1)
        layout.add_widget(spacer)

        data_input.add_widget(layout)

        spacer_right = SpacerBox(size_hint_x=0.2)
        data_input.add_widget(spacer_right)

        # add everything to this Screen
        self.add_widget(data_input)

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
        
    def on_pot_change(self, slider, value):
        self.pot_label.text = f"{int(value)}"

    def on_thirst_change(self, slider, value):
        # you’ll probably want to move these into SowSeedScreen later
        self.thirsty_label.text = f"{int(value)}"

    def on_hunger_change(self, slider, value):
        self.hunger_label.text = f"{int(value)}"


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
            "days_to_flower_est": int(self.days_to_flower.text) + 14 if self.days_to_flower.text else None,
            "days_to_harvest_est": (int(self.days_to_flower.text) * 2 )+14 if self.days_to_flower.text else None,
            "pot_size_l": float(self.pot_slider.value),
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