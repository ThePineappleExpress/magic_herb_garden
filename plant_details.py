from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
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
    angle = NumericProperty(45)
    pass

class LogoLabel1(Label):
    pass


class LogoLabel2(Label):
    pass


class LogoLabel3(Label):
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

class PlantDetailsScreen(Screen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        garden_view = WrapperBox(orientation="horizontal")
        self.add_widget(garden_view)