
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
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
