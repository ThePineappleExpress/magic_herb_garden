from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.properties import ListProperty, StringProperty
from buttons import ButtonTransparent, ButtonDarkGreen
class CustomDropdown(BoxLayout):
    options = ListProperty([])
    selected = StringProperty("")

    def __init__(self, options=None, **kwargs):
        text = kwargs.pop("text", None)
        values = kwargs.pop("values", None)
        app = App.get_running_app()
        super().__init__(orientation="horizontal", **kwargs)
        self.dropdown = DropDown()
        self.options = values if values is not None else (options or [])
        if text is not None:
            self.selected = text
        self.main_button = ButtonTransparent(text=self.selected or (self.options[0] if self.options else "Select"))
        self.main_button.bind(on_release=self.open_dropdown)
        self.add_widget(self.main_button)
        self._populate_dropdown()

    def _populate_dropdown(self):
        self.dropdown.clear_widgets()
        for opt in self.options:
            btn = ButtonDarkGreen(text=opt)
            btn.size_hint_y = None
            btn.size_hint_x = 1
            btn.height = dp(40)
            btn.bind(on_release=lambda btn: self.select_option(btn.text))
            self.dropdown.add_widget(btn)

    def open_dropdown(self, *args):
        self.dropdown.open(self.main_button)

    def select_option(self, value):
        self.selected = value
        self.main_button.text = value
        self.dropdown.dismiss()

    def on_options(self, instance, value):
        self._populate_dropdown()
