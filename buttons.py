
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
from kivy.properties import BooleanProperty, ListProperty
from kivy.graphics import Color, Triangle as KvTriangle
import hover_manager


# Simple HoverBehavior mixin: sets `hovered` and calls `on_enter`/`on_leave`.
# Uses the centralized hover_manager for a single Window.mouse_pos callback.
class HoverBehavior:
    hovered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        hover_manager.register(self)

    def on_parent(self, instance, parent):
        """Unregister when removed from tree, re-register when added."""
        if parent is None:
            hover_manager.unregister(self)
        else:
            hover_manager.register(self)

    def on_enter(self):
        pass

    def on_leave(self):
        pass


class HoverButton(HoverBehavior, Button):
    hover_background_color = ListProperty([0.773, 0.847, 0.427, 1])
    normal_background_color = ListProperty([0.12, 0.172, 0.153, 1])

    def on_enter(self):
        self.background_color = list(self.hover_background_color)

    def on_leave(self):
        self.background_color = list(self.normal_background_color)


class HoverToggle(HoverBehavior, ToggleButton):
    hover_background_color = ListProperty([0.773, 0.847, 0.427, 1])
    normal_background_color = ListProperty([0, 0, 0, 0])

    def on_enter(self):
        if self.state == 'normal':
            self.background_color = list(self.hover_background_color)

    def on_leave(self):
        if self.state == 'normal':
            self.background_color = list(self.normal_background_color)


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


class SortDirButton(HoverToggle):
    """Toggle button that draws a filled up-triangle (ascending) or down-triangle (descending)."""

    def __init__(self, **kwargs):
        kwargs.setdefault('text', '')
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, state=self._redraw)

    def _redraw(self, *args):
        self.canvas.after.clear()
        with self.canvas.after:
            app = App.get_running_app()
            if app and hasattr(app, 'theme'):
                Color(*app.theme.color_highlight)
            else:
                Color(1, 1, 1, 1)
            cx = self.x + self.width / 2
            cy = self.y + self.height / 2
            r = min(self.width, self.height) * 0.28
            if self.state == 'normal':
                # Up-pointing triangle — ascending
                KvTriangle(points=[
                    cx,     cy + r,
                    cx - r, cy - r,
                    cx + r, cy - r,
                ])
            else:
                # Down-pointing triangle — descending
                KvTriangle(points=[
                    cx,     cy - r,
                    cx - r, cy + r,
                    cx + r, cy + r,
                ])


class SelectorDropdown(Spinner):
    pass


class PasswordEyeToggle(HoverButton):
    """Toggle button that shows/hides a linked TextInput's password mask."""

    def __init__(self, text_input=None, **kwargs):
        kwargs.setdefault("text", "Show")
        kwargs.setdefault("size_hint_x", None)
        kwargs.setdefault("width", 80)
        super().__init__(**kwargs)
        self._text_input = text_input
        self._visible = False
        self.bind(on_press=self._toggle)

    def _toggle(self, *args):
        if self._text_input is None:
            return
        self._visible = not self._visible
        self._text_input.password = not self._visible
        self.text = "Hide" if self._visible else "Show"

    def reset(self):
        """Reset to hidden state."""
        self._visible = False
        if self._text_input:
            self._text_input.password = True
        self.text = "Show"

    @property
    def text_input(self):
        return self._text_input

    @text_input.setter
    def text_input(self, value):
        self._text_input = value