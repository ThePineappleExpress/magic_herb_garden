from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from fx import SmokeShaderWidget

class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        # Add the smoke shader as the first (background) widget
        self.layout.add_widget(SmokeShaderWidget(size_hint=(1, 1), pos_hint={'x': -0.5, 'y': -0.5}))
        self.add_widget(self.layout)

    def add_content(self, widget):
        # Add your actual content on top of the shader
        self.layout.add_widget(widget)