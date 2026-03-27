"""list_screen.py - Base class for list screens (garden list, plant list).

Provides the shared layout scaffold (sidebar, header, sort/filter toolbar,
legend, RecycleView area, footer) and sort/filter/search logic.  Subclasses
only need to specify their column legends, sort mappings, buttons, and
data-loading/action methods.
"""

from kivy.app import App
from kivy.uix.togglebutton import ToggleButton

from boxes import (
    TitleBox, WrapperBox, ContentBox, ItemBox, SpacerBox,
)
from buttons import ButtonGreen, ButtonRed, ButtonYellow, SortDirButton
from labels import FieldLabel, TitleLabel, ListSubLabel
from text_inputs import MedTextInput
from custom_dropdown import CustomDropdown
from screens import BaseScreen
from ui_builders import create_stripes_logo
import lang


class BaseListScreen(BaseScreen):
    """Reusable base for any screen that shows a sorted/filtered RecycleView.

    Subclasses must set or override:
        _title_text         -- lang constant for the sidebar title
        _sort_options       -- list of sort option labels
        _sort_label_to_key  -- dict mapping sort labels → data keys
        _default_sort_key   -- initial sort key
        _default_ascending  -- initial sort direction
        _searchable_fields  -- list of data keys to search across
        _legend_columns     -- list of (text, size_hint_x, halign) tuples
        _header_buttons     -- list of (text, ButtonClass, callback, size_hint_x) tuples
        _footer_buttons     -- list of (text, ButtonClass, callback, size_hint_x, spacer_before)
        _list_widget_class  -- RecycleView subclass to instantiate
    """

    _title_text = ""
    _sort_options = []
    _sort_label_to_key = {}
    _default_sort_key = "name"
    _default_ascending = True
    _searchable_fields = []
    _legend_columns = []
    _header_buttons = []
    _footer_buttons = []
    _list_widget_class = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._all_items = []
        self._sort_key = self._default_sort_key
        self._sort_ascending = self._default_ascending

        screen_wrapper = WrapperBox(orientation="horizontal", size_hint_x=1)

        # -- Left sidebar --
        sidebar = SpacerBox(size_hint_x=0.2)
        sidebar.add_widget(create_stripes_logo())
        sidebar.add_widget(SpacerBox(size_hint_x=0.3))
        title = TitleLabel(
            text=self._title_text.format(color=TitleLabel().hex_color)
        )
        sidebar.add_widget(title)
        sidebar.add_widget(SpacerBox(size_hint_x=0.3))
        screen_wrapper.add_widget(sidebar)

        # -- Right content area --
        content = ContentBox(orientation="vertical", size_hint=(1, 1))

        # Header
        header = TitleBox(orientation="horizontal", size_hint_y=0.1)
        btn_width = sum(b[3] for b in self._header_buttons)
        header.add_widget(SpacerBox(size_hint_x=1.0 - btn_width))
        side_menu = ItemBox(orientation="horizontal", size_hint_x=btn_width)
        for text, btn_cls, callback, sx in self._header_buttons:
            btn = btn_cls(text=text, size_hint_x=sx)
            btn.bind(on_release=callback)
            side_menu.add_widget(btn)
        header.add_widget(side_menu)
        content.add_widget(header)

        content.add_widget(SpacerBox(size_hint_y=0.02))

        # Sort / Search / Filter toolbar
        toolbar = ContentBox(
            orientation="horizontal", size_hint_y=None, height="40dp",
        )
        sort_label = FieldLabel(text=lang.SORT_BY, size_hint_x=None, width="100dp")
        toolbar.add_widget(sort_label)
        self.sort_dropdown = CustomDropdown(
            options=self._sort_options, size_hint_x=0.2,
        )
        default_label = next(
            (k for k, v in self._sort_label_to_key.items()
             if v == self._default_sort_key),
            self._sort_options[0] if self._sort_options else "",
        )
        self.sort_dropdown.selected = default_label
        self.sort_dropdown.main_button.text = default_label
        self.sort_dropdown.bind(selected=self._on_sort_changed)
        toolbar.add_widget(self.sort_dropdown)

        self.sort_dir_btn = SortDirButton(
            size_hint_x=None, width="44dp",
            state="down" if not self._default_ascending else "normal",
        )
        self.sort_dir_btn.bind(state=self._on_sort_dir_toggle)
        toolbar.add_widget(self.sort_dir_btn)
        toolbar.add_widget(SpacerBox(size_hint_x=0.05))

        self.search_input = MedTextInput(
            hint_text=lang.SEARCH_HINT, size_hint_x=0.3, multiline=False,
        )
        self.search_input.bind(text=self._on_search_text)
        toolbar.add_widget(self.search_input)
        toolbar.add_widget(SpacerBox(size_hint_x=0.05))

        self.active_toggle = ToggleButton(
            text=lang.FILTER_ACTIVE_ONLY, size_hint_x=0.2,
        )
        self.active_toggle.bind(on_press=self._on_active_toggle)
        toolbar.add_widget(self.active_toggle)
        content.add_widget(toolbar)

        content.add_widget(SpacerBox(size_hint_y=0.02))

        # Legend row
        legend = ContentBox(
            orientation="horizontal", size_hint_y=None, height="28dp",
        )
        legend.add_widget(SpacerBox(size_hint_x=0.02))
        for text, sx, halign in self._legend_columns:
            kw = {"text": text, "size_hint_x": sx, "halign": halign, "valign": "middle"}
            if halign == "left":
                kw["padding"] = (10, 0, 0, 0)
            legend.add_widget(ListSubLabel(**kw))
        legend.add_widget(SpacerBox(size_hint_x=0.02))
        content.add_widget(legend)

        # RecycleView list
        list_area = ItemBox(orientation="horizontal", size_hint_y=1)
        list_area.add_widget(SpacerBox(size_hint_x=0.02))
        self.list_widget = self._list_widget_class(size_hint_x=1)
        self.list_widget._owner = self
        list_area.add_widget(self.list_widget)
        list_area.add_widget(SpacerBox(size_hint_x=0.02))
        content.add_widget(list_area)

        content.add_widget(SpacerBox(size_hint_y=0.02))

        # Footer
        footer = ContentBox(orientation="horizontal", size_hint_y=0.1)
        for text, btn_cls, callback, sx, spacer in self._footer_buttons:
            if spacer:
                footer.add_widget(SpacerBox(size_hint_x=spacer))
            btn = btn_cls(text=text)
            if sx:
                btn.size_hint_x = sx
            btn.bind(on_press=callback)
            footer.add_widget(btn)
        content.add_widget(footer)

        screen_wrapper.add_widget(content)
        self.add_content(screen_wrapper)

    # -- Sort / Filter logic (shared) ------------------------------------------

    def _is_active(self, item):
        """Override to define the active-only filter predicate."""
        return True

    def _apply_filters(self):
        """Apply search, active-only filter, and sort to _all_items."""
        items = list(self._all_items)

        query = getattr(self, "search_input", None)
        search_text = query.text.strip().lower() if query else ""
        if search_text:
            fields = self._searchable_fields
            items = [
                it for it in items
                if any(search_text in (it.get(f) or "").lower() for f in fields)
            ]

        active_only = getattr(self, "active_toggle", None)
        if active_only and active_only.state == "down":
            items = [it for it in items if self._is_active(it)]

        key = self._sort_key
        ascending = self._sort_ascending

        def sort_val(it):
            v = it.get(key) or ""
            if isinstance(v, str):
                try:
                    return (0, float(v))
                except (ValueError, TypeError):
                    return (1, v.lower())
            return (1, str(v).lower())

        items.sort(key=sort_val, reverse=not ascending)
        self.list_widget.data = items

    def _on_sort_changed(self, instance, value):
        self._sort_key = self._sort_label_to_key.get(value, self._default_sort_key)
        if value == lang.SORT_NEXT_EVENT:
            self._sort_ascending = True
            self.sort_dir_btn.state = "normal"
        elif value == lang.SORT_LAST_EVENT:
            self._sort_ascending = False
            self.sort_dir_btn.state = "down"
        self._apply_filters()

    def _on_sort_dir_toggle(self, instance, state):
        self._sort_ascending = state != "down"
        self._apply_filters()

    def _on_search_text(self, instance, value):
        self._apply_filters()

    def _on_active_toggle(self, instance):
        self._apply_filters()

    # -- Selection helpers (shared) --------------------------------------------

    def get_selected_index(self):
        lm = self.list_widget.layout_manager
        if not lm or not lm.selected_nodes:
            return None
        return lm.selected_nodes[0]

    def get_selected_item(self):
        idx = self.get_selected_index()
        if idx is None:
            return None
        return self.list_widget.data[idx]
