
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, Rectangle
from kivy.properties import ListProperty, BooleanProperty


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
class EventBox(ItemBox):
    hovered = BooleanProperty(False)
    normal_text_color = ListProperty([1, 1, 1, 1])
    hover_text_color = ListProperty([0, 0, 0, 1])
    normal_bg_color = ListProperty([0, 0, 0, 0])
    hover_bg_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        app = App.get_running_app()
        if app and hasattr(app, "theme"):
            self.normal_text_color = app.theme.nice_yellow
            self.hover_text_color = app.theme.dark_gray
            self.normal_bg_color = app.theme.black_transparent
            self.hover_bg_color = app.theme.nice_green
        Window.bind(mouse_pos=self._on_mouse_pos)
        self.bind(hovered=self._apply_hover_state)

    def on_parent(self, instance, parent):
        if parent is None:
            Window.unbind(mouse_pos=self._on_mouse_pos)

    def _on_mouse_pos(self, _window, pos):
        if not self.get_root_window():
            return
        is_hover = self.collide_point(*self.to_widget(*pos))
        if self.hovered != is_hover:
            self.hovered = is_hover

    def add_widget(self, widget, *args, **kwargs):
        super().add_widget(widget, *args, **kwargs)
        self._apply_hover_state()

    def _apply_hover_state(self, *_args):
        color = self.hover_text_color if self.hovered else self.normal_text_color
        for child in self.children:
            if hasattr(child, "color"):
                child.color = color
class RedBox(ContentBox):
    pass
class YellowBox(ContentBox):
    pass
class GreenBox(ContentBox):
    pass
class DarkBox(ContentBox):
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
            self.normal_bg_color = app.theme.black_transparent
            self.selected_bg_color = app.theme.nice_green
            self.normal_text_color = app.theme.off_white
            self.selected_text_color = app.theme.dark_gray

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
