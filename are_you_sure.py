from kivy.app import App
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from helpers import on_plant_seed, go_to_garden
from labels import FieldLabel, PromptLabel
from buttons import ButtonGreen, ButtonRed
from boxes import WrapperBox, ContentBox, ItemBox, TitleBox, RedBox, YellowBox, GreenBox, SpacerBox
from screens import BaseScreen

class AreYouSure(BaseScreen):
    theme = ObjectProperty(None)
    confirm_callback = ObjectProperty("")
    prompt_text = StringProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        content_wrapper = WrapperBox(orientation="horizontal")

        spacer = SpacerBox()
        content_wrapper.add_widget(spacer)
        
        prompt_wrapper = WrapperBox(orientation="vertical")
        content_wrapper.add_widget(prompt_wrapper)

        spacer = SpacerBox()
        prompt_wrapper.add_widget(spacer)

        prompt_box = ContentBox( orientation="vertical", size_hint=(0.6, 0.6), pos_hint={"center_x": 0.5, "center_y": 0.5})
        prompt_wrapper.add_widget(prompt_box)

        spacer = SpacerBox(size_hint_y=0.01)
        prompt_box.add_widget(spacer)

        title_box = ItemBox(orientation="horizontal", size_hint_y=0.2)
        prompt_box.add_widget(title_box)

        title_label = FieldLabel(text="Are you sure?", halign="center", valign="middle")
        title_label.font_name = app.theme.font_logo_2
        title_label.font_size = app.theme.title_size
        title_label.color = app.theme.nice_yellow
        title_box.add_widget(title_label)

        spacer = SpacerBox(size_hint_y=0.01)
        prompt_box.add_widget(spacer)

        text_box = ItemBox(orientation="horizontal", size_hint_y=0.4)
        text_label = PromptLabel(text=self.prompt_text, halign="left", valign="middle")
        self.bind(prompt_text=text_label.setter("text"))
        text_label.font_size = app.theme.body_size
        text_label.color = app.theme.off_white
        text_box.add_widget(text_label)
        prompt_box.add_widget(text_box)

        spacer = SpacerBox(size_hint_y=0.02)
        prompt_box.add_widget(spacer)

        button_box = ItemBox(orientation="horizontal", size_hint_y=0.3)
        prompt_box.add_widget(button_box)
        confirm_button = ButtonGreen(text="Yes")
        confirm_button.bind(on_release=self.on_confirm)
        button_box.add_widget(confirm_button)
        cancel_button = ButtonRed(text="No")
        cancel_button.bind(on_release=app.go_back)
        button_box.add_widget(cancel_button)

        spacer = SpacerBox()
        prompt_wrapper.add_widget(spacer)

        spacer = SpacerBox()
        content_wrapper.add_widget(spacer)

        self.add_widget(content_wrapper)

    def on_confirm(self, *args):
        if hasattr(self, "confirm_callback") and self.confirm_callback:
            self.confirm_callback()