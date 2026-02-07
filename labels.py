from kivy.app import App
from kivy.uix.label import Label
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty

from helpers import rgba_to_hex

class GardenLabel(Label):
    pass
class LogoLabel1(Label):
    pass
class LogoLabel2(Label):
    pass
class LogoLabel3(Label):
    pass
class ListLabel(Label):
    pass
class ListTitleLabel(Label):
    pass
class ListSubLabel(Label):
    pass
class NutrientLabel(Label):
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
            
class FieldLabel(Label):
    pass
class HintLabel(Label):
    pass

class PromptLabel(Label):
    pass
class WarningTitleLabel(Label):
    pass
class WarningLabel(Label):
    pass