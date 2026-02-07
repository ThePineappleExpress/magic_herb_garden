
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty


# Simple HoverBehavior mixin: sets `hovered` and calls `on_enter`/`on_leave`.
class HoverBehavior:
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            return
        self.hovered = inside
        if inside:
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self):
        pass

    def on_leave(self):
        pass


class HoverButton(HoverBehavior, Button):
    app = App.get_running_app()
    hover_background_color = ListProperty([0.773, 0.847, 0.427, 1])
    _orig_background_color = None

    def on_enter(self):

        if self._orig_background_color is None:
            self._orig_background_color = list(self.background_color)
        self.background_color = list(self.hover_background_color)


    def on_leave(self):
        if self._orig_background_color is not None:
            self.background_color = list(self._orig_background_color)



class HoverToggle(HoverBehavior, ToggleButton):
    hover_background_color = ListProperty([0.773, 0.847, 0.427, 1])
    _orig_background_color = None

    def on_enter(self):
        # Only apply hover styling when the toggle is in the normal (unpressed) state.
        if self.state == 'normal':
            if self._orig_background_color is None:
                self._orig_background_color = list(self.background_color)
            self.background_color = list(self.hover_background_color)


    def on_leave(self):
        # Restore original background only when leaving while in normal state.
        if self.state == 'normal' and self._orig_background_color is not None:
            self.background_color = list(self._orig_background_color)
            self._orig_background_color = None



class ButtonGreen(HoverButton):
    pass


class ButtonYellow(HoverButton):
    pass


class ButtonRed(HoverButton):
    pass


class ButtonBlue(HoverButton):
    pass


class ButtonPurple(HoverButton):
    pass


class ButtonDarkGreen(HoverButton):
    pass


class ButtonTransparent(HoverButton):
    pass


class SuggestionButton(HoverButton):
    pass


class NutrientButton(HoverToggle):
    pass

class GraphButton(HoverToggle):
    pass
class ResetButton(HoverToggle):
    pass


class SelectorDropdown(Spinner):
    pass