
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty, BooleanProperty
import hover_manager


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
class EventBox(BoxLayout):
    hovered = BooleanProperty(False)
    normal_text_color = ListProperty([1, 1, 1, 1])
    hover_text_color = ListProperty([0, 0, 0, 1])
    normal_bg_color = ListProperty([0, 0, 0, 0])
    hover_bg_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app and hasattr(app, "theme"):
            self.normal_text_color = app.theme.color_event_box_text
            self.hover_text_color = app.theme.color_event_box_hover_text
            self.normal_bg_color = app.theme.color_transparent
            self.hover_bg_color = app.theme.color_event_box_hover_bg
        hover_manager.register(self)
        self.bind(hovered=self._apply_hover_state)

    def on_parent(self, instance, parent):
        if parent is None:
            hover_manager.unregister(self)
        else:
            hover_manager.register(self)

    def on_enter(self):
        self.hovered = True

    def on_leave(self):
        self.hovered = False

    def add_widget(self, widget, *args, **kwargs):
        super().add_widget(widget, *args, **kwargs)
        self._apply_hover_state()

    def _apply_hover_state(self, *_args):
        color = self.hover_text_color if self.hovered else self.normal_text_color
        for child in self.children:
            if hasattr(child, "color"):
                child.color = color
class RedBox(BoxLayout):
    pass
class YellowBox(BoxLayout):
    pass
class GreenBox(BoxLayout):
    pass
class DarkBox(BoxLayout):
    pass
class LightBox(BoxLayout):
    pass
class SelectableRecycleBoxLayout(LayoutSelectionBehavior, RecycleBoxLayout):
    pass
class SelectableBoxLayout(RecycleDataViewBehavior, BoxLayout):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super().refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            rv = self.parent.parent 
            if rv.layout_manager:
                rv.layout_manager.select_node(self.index)
            if touch.is_double_tap and hasattr(rv, 'on_double_tap'):
                rv.on_double_tap(self.index)
            return True

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected

class SelectableEventBox(ButtonBehavior, BoxLayout):
    selected = BooleanProperty(False)
    normal_bg_color = ListProperty([0, 0, 0, 0])
    selected_bg_color = ListProperty([0.3, 0.7, 0.4, 0.7])
    normal_text_color = ListProperty([1, 1, 1, 1])
    selected_text_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app and hasattr(app, "theme"):
            self.normal_bg_color = app.theme.color_transparent
            self.selected_bg_color = app.theme.color_selectable_selected_bg
            self.normal_text_color = app.theme.color_label_subtitle
            self.selected_text_color = app.theme.color_selectable_selected_text

        with self.canvas.before:
            self._bg_color = Color(*self.normal_bg_color)
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update_rect, size=self._update_rect)
        self.bind(selected=self._apply_selected_state)
        self.bind(normal_bg_color=self._apply_selected_state)
        self.bind(selected_bg_color=self._apply_selected_state)
        self.bind(normal_text_color=self._apply_selected_state)
        self.bind(selected_text_color=self._apply_selected_state)

    def _update_rect(self, *_args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    def _apply_selected_state(self, *_args):
        bg = self.selected_bg_color if self.selected else self.normal_bg_color
        fg = self.selected_text_color if self.selected else self.normal_text_color
        self._bg_color.rgba = bg
        self._set_label_colors(self, fg)

    def _set_label_colors(self, widget, color):
        for child in widget.children:
            if hasattr(child, "color"):
                child.color = color
            self._set_label_colors(child, color)
