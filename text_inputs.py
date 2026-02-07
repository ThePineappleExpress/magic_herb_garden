import re
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.properties import ListProperty
class NumTextInput(TextInput):
    max_chars = 6
    multiline=False
    input_filter="float"
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        if allowed <= 0:
            return
        substring = substring[:allowed]
        super().insert_text(substring, from_undo=from_undo)
class DaysTextInput(TextInput):
    max_chars = 4
    multiline=False
    input_filter="int"
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        if allowed <= 0:
            return
        substring = substring[:allowed]
        super().insert_text(substring, from_undo=from_undo)
class MedTextInput(TextInput):
    max_chars = 32
    multiline=False
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        if allowed <= 0:
            return
        substring = substring[:allowed]
        super().insert_text(substring, from_undo=from_undo)
class LargeTextInput(TextInput):
    max_chars = 128
    multiline=True
    allowed_chars = re.compile(r'^[a-zA-Z0-9 \-\_\.\,\'\"\+\!\?\@\#\$\(\)]*$')
    size_hint_y = None
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def insert_text(self, substring, from_undo=False):
        allowed = max(0, self.max_chars - len(self.text))
        filtered = ''.join(c for c in substring if self.allowed_chars.match(c))
        if allowed <= 0:
            return
        substring = filtered[:allowed]
        super().insert_text(substring, from_undo=from_undo)

