import sys, os
from datetime import date
from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
import xml.etree.ElementTree as ET
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget
from kivy.graphics.svg import Svg
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale

from labels import TitleLabel, FieldLabel
from storage import get_plants_for_garden, save_plants_for_garden, remove_plant_from_garden, load_plant_events
import lang
from helpers import on_plant_seed, get_difference_days
from boxes import TitleBox, WrapperBox, ContentBox, ItemBox, SpacerBox, RedBox, YellowBox, GreenBox, SelectableBoxLayout, SelectableRecycleBoxLayout
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import NumTextInput, MedTextInput, LargeTextInput
from custom_dropdown import CustomDropdown
from screens import BaseScreen
class LeafIcon(Widget):
    source = StringProperty("")
    _svg = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(source=self._on_source, pos=self._redraw, size=self._redraw)

    def _on_source(self, *args):
        # Recreate Svg only when source changes
        self._svg = Svg(self.source) if self.source else None
        self._redraw()

    def _redraw(self, *args):
        self.canvas.clear()
        if not self._svg:
            return

        svg = self._svg
        # Guard against zero sizes
        if self.height <= 0 or self.width <= 0 or svg.width <= 0 or svg.height <= 0:
            return

        # Scale to fit height, preserve aspect ratio
        scale = (self.height / svg.height) / 1.5
        # Optionally center horizontally within the box
        scaled_w = svg.width * scale
        scaled_h = svg.height * scale
        x = self.x + (self.width - scaled_w) * 0.5
        y = self.y + (self.height - scaled_h) * 0.6

        self.canvas.add(PushMatrix())
        self.canvas.add(Translate(x, y))
        self.canvas.add(Scale(scale, scale, 1))
        self.canvas.add(svg)
        self.canvas.add(PopMatrix())
class PlantListView(RecycleView):
    genes = StringProperty("")
    genes_icon = StringProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"  # uses the kv rule above
        self.data = []                    # will fill from GardenViewScreen
        self._owner = None                # set by GardenViewScreen

    def on_double_tap(self, index):
        """Called by SelectableBoxLayout on double-tap; opens plant details."""
        if self._owner and 0 <= index < len(self.data):
            self._owner.on_details_button()

    def on_genes(self, instance, value):
        if value == "Sativa":
            self.genes_icon = "S"
        elif value == "Indica":
            self.genes_icon = "I"
        elif value == "Hybrid":
            self.genes_icon = "H"
        else:
            self.genes_icon = "?"

class GardenViewScreen(BaseScreen):
    theme = ObjectProperty(None)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._all_plants = []
        garden_view_screen = WrapperBox(orientation="horizontal", size_hint_x=1)
        spacer_left = SpacerBox(size_hint_x=0.2)
        stripes_holder = ContentBox(orientation="horizontal")
        stripe_0 = ItemBox(size_hint_x=0.45)
        stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox()
        stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox()
        stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox()
        stripes_holder.add_widget(stripe_3)
        stripe_4 = ItemBox(size_hint_x=0.45)
        stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text=lang.SCREEN_TITLE_GARDEN.format(color=TitleLabel().hex_color))
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        garden_view_screen.add_widget(spacer_left)

        content_wrapper = ContentBox(orientation="vertical", size_hint=(1, 1))

        header = TitleBox(orientation="horizontal", size_hint_y=0.1)

        spacer = SpacerBox(size_hint_x=0.8)
        header.add_widget(spacer)
        side_menu = ItemBox(orientation='horizontal', size_hint_x=0.2)
        option_btn = ButtonYellow(text=lang.OPTIONS, size_hint_x=0.1)
        option_btn.bind(on_release=self.on_options)
        side_menu.add_widget(option_btn)
        exit_btn = ButtonRed(text=lang.EXIT_GARDEN, size_hint_x=0.1)
        exit_btn.bind(on_release=self.on_garden_exit)
        side_menu.add_widget(exit_btn)

        header.add_widget(side_menu)

        content_wrapper.add_widget(header)

        content_wrapper.add_widget(SpacerBox(size_hint_y=0.02))

        # ── Sort / Search / Filter toolbar ──
        toolbar = ContentBox(orientation="horizontal", size_hint_y=None, height="40dp")

        # Sort dropdown
        self._sort_key = "strain"
        self._sort_ascending = True
        sort_options = [
            lang.SORT_NAME, lang.SORT_BREEDER, lang.SORT_DATE_PLANTED,
            lang.SORT_DAYS_TO_HARVEST, lang.SORT_DAYS_TO_WATER, lang.SORT_MEDIUM,
        ]
        self._sort_label_to_key = {
            lang.SORT_NAME: "strain",
            lang.SORT_BREEDER: "name",
            lang.SORT_DATE_PLANTED: "date_planted",
            lang.SORT_DAYS_TO_HARVEST: "harvest_status",
            lang.SORT_DAYS_TO_WATER: "last_watering",
            lang.SORT_MEDIUM: "medium",
        }
        sort_label = FieldLabel(text=lang.SORT_BY, size_hint_x=None, width="60dp")
        toolbar.add_widget(sort_label)
        self.sort_dropdown = CustomDropdown(
            options=sort_options,
            size_hint_x=0.2,
        )
        self.sort_dropdown.selected = lang.SORT_NAME
        self.sort_dropdown.main_button.text = lang.SORT_NAME
        self.sort_dropdown.bind(selected=self._on_sort_changed)
        toolbar.add_widget(self.sort_dropdown)

        # Asc / Desc toggle
        self.sort_dir_btn = ToggleButton(
            text=lang.SORT_ASCENDING, size_hint_x=None, width="100dp",
        )
        self.sort_dir_btn.bind(on_press=self._on_sort_dir_toggle)
        toolbar.add_widget(self.sort_dir_btn)

        toolbar.add_widget(SpacerBox(size_hint_x=0.05))

        # Search input
        self.search_input = MedTextInput(
            hint_text=lang.SEARCH_HINT, size_hint_x=0.3,
            multiline=False,
        )
        self.search_input.bind(text=self._on_search_text)
        toolbar.add_widget(self.search_input)

        toolbar.add_widget(SpacerBox(size_hint_x=0.05))

        # Active-only toggle
        self.active_toggle = ToggleButton(
            text=lang.FILTER_ACTIVE_ONLY, size_hint_x=0.2,
        )
        self.active_toggle.bind(on_press=self._on_active_toggle)
        toolbar.add_widget(self.active_toggle)

        content_wrapper.add_widget(toolbar)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)
        
        garden_list = ItemBox(orientation="horizontal", size_hint_y=1)

        spacer_box = SpacerBox(size_hint_x=0.02)
        garden_list.add_widget(spacer_box)

        self.plant_list = PlantListView(size_hint_x=1)
        self.plant_list._owner = self
        garden_list.add_widget(self.plant_list)

        spacer_box = SpacerBox(size_hint_x=0.02)
        garden_list.add_widget(spacer_box)

        content_wrapper.add_widget(garden_list)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        garden_footer = ContentBox(orientation="horizontal", size_hint_y=0.1)
        spacer_box = SpacerBox(size_hint_x=0.8)
        garden_footer.add_widget(spacer_box)
        add_plant_btn = ButtonGreen(text=lang.ADD_PLANT)
        add_plant_btn.bind(on_press=on_plant_seed)
        garden_footer.add_widget(add_plant_btn)
        view_selected_btn = ButtonYellow(text=lang.VIEW_SELECTED_PLANT)
        view_selected_btn.bind(on_release=self.on_details_button)
        view_selected_btn.bind(on_release=self.on_view_selected)
        garden_footer.add_widget(view_selected_btn)
        delete_selected_btn = ButtonRed(text=lang.DELETE_SELECTED_PLANT)
        delete_selected_btn.bind(on_release=self.on_delete_pressed)
        garden_footer.add_widget(delete_selected_btn)

        content_wrapper.add_widget(garden_footer)

        garden_view_screen.add_widget(content_wrapper)

        # Use add_content to ensure content is above the shader background
        self.add_content(garden_view_screen)
        self.refresh_plants()

        
    def on_delete_pressed(self, instance):
        app = App.get_running_app()
        are_you_sure = app.screen.get_screen("are_you_sure")
        are_you_sure.confirm_callback = lambda *_: self.on_delete_selected()
        are_you_sure.prompt_text = lang.MSG_CONFIRM_DELETE_PLANT
        app.previous_screen = app.screen.current
        app.screen.current = "are_you_sure"

    def on_options(self, instance):
        app = App.get_running_app()
        app.previous_screen = app.screen.current
        app.screen.current = "settings"

    def on_garden_exit(self, instance):
        app = App.get_running_app()
        app.previous_screen = app.screen.current
        app.screen.current = "select_garden"

    def refresh_plants(self):
        app = App.get_running_app()
        garden_id = getattr(app, 'current_garden_id', None)
        plants = get_plants_for_garden(garden_id) if garden_id else []
        today = date.today()
        data = []
        for p in plants:
            if not isinstance(p, dict):
                continue
            # basic text fields
            plant_id = p.get("id")
            name = p.get("name", "")
            strain = p.get("strain", "")
            notes = p.get("notes", "")
            genes = p.get("genes", "")
            date_planted  = p.get("date_planted", "")
            self.plant_event = load_plant_events(str(plant_id)) if plant_id else None
            events = (self.plant_event or {}).get("events", [])
            last_event = events[-1] if events else None
            last_event_ts = last_event.get("ts") if isinstance(last_event, dict) else None

            last_watering = get_difference_days(today, last_event_ts) if last_event_ts else None
            if last_watering is None:
                last_watering = lang.DASH
            else:
                last_watering = str(last_watering)
            next_watering = lang.DASH
            flower_status = lang.DASH
            harvest_status = lang.DASH

            # example: rough days to flower based on estimate and date_planted
            dt_str = p.get("date_planted")
            base_f = p.get("days_to_flower")
            try:
                base_f = int(base_f) if base_f is not None else 0
            except (ValueError, TypeError):
                base_f = 0
            penalty = int(p.get("penalty", 0) or 0)
            est_f = base_f + 14 + penalty
            est_h = est_f * 2
            if dt_str and est_h:
                try:
                    y, m, d = map(int, dt_str.split("-"))
                    planted = date(y, m, d)
                    days_since = (today - planted).days
                    days_left = est_h - days_since
                    if days_left >= 0:
                        harvest_status = f"{days_left}"
                    else:
                        harvest_status = lang.STATUS_HARVESTED
                except Exception:
                    harvest_status = f"{est_h}"

            if dt_str and est_f:
                try:
                    y, m, d = map(int, dt_str.split("-"))
                    planted = date(y, m, d)
                    days_since = (today - planted).days
                    days_left = est_f - days_since
                    if days_left > 0:
                        flower_status = f"{days_left}"
                    elif days_left <= 0 and harvest_status != "Harvested!":
                        flower_status = lang.STATUS_FLOWERING
                    elif days_left <= 0 and harvest_status == lang.STATUS_HARVESTED:
                        flower_status = lang.STATUS_HARVESTED
                except Exception:
                    flower_status = f"{est_f}"
            medium = p.get("medium")
            stage = p.get("stage", "")

            # Override statuses based on stored stage field (set by flip/harvest events)
            if stage == "harvested":
                harvest_status = lang.STATUS_HARVESTED
                flower_status = lang.STATUS_HARVESTED
            elif stage == "flowering":
                if flower_status not in (lang.STATUS_FLOWERING, lang.STATUS_HARVESTED):
                    flower_status = lang.STATUS_FLOWERING


            data.append({
                "id": plant_id,
                "genes": genes,
                "name": name,
                "strain": strain,
                "notes": notes,
                "medium": medium,
                "last_watering": last_watering,
                "next_watering": next_watering,
                "flower_status": flower_status,
                "harvest_status": harvest_status,
                "date_planted": date_planted,
            })

        self._all_plants = data
        self._apply_filters()

    def _apply_filters(self):
        """Apply search, active-only filter, and sort to _all_plants → plant_list.data."""
        items = list(self._all_plants)

        # Search filter
        query = getattr(self, 'search_input', None)
        search_text = query.text.strip().lower() if query else ""
        if search_text:
            items = [
                p for p in items
                if search_text in (p.get("strain") or "").lower()
                or search_text in (p.get("name") or "").lower()
                or search_text in (p.get("notes") or "").lower()
                or search_text in (p.get("medium") or "").lower()
                or search_text in (p.get("genes") or "").lower()
            ]

        # Active-only filter
        active_only = getattr(self, 'active_toggle', None)
        if active_only and active_only.state == "down":
            items = [
                p for p in items
                if p.get("harvest_status") != lang.STATUS_HARVESTED
            ]

        # Sort
        key = getattr(self, '_sort_key', 'strain')
        ascending = getattr(self, '_sort_ascending', True)

        def sort_val(p):
            v = p.get(key) or ""
            if isinstance(v, str):
                # Try numeric sort for numeric string values
                try:
                    return (0, float(v))
                except (ValueError, TypeError):
                    return (1, v.lower())
            return (1, str(v).lower())

        items.sort(key=sort_val, reverse=not ascending)
        self.plant_list.data = items

    def _on_sort_changed(self, instance, value):
        self._sort_key = self._sort_label_to_key.get(value, "strain")
        self._apply_filters()

    def _on_sort_dir_toggle(self, instance):
        if instance.state == "down":
            self._sort_ascending = False
            instance.text = lang.SORT_DESCENDING
        else:
            self._sort_ascending = True
            instance.text = lang.SORT_ASCENDING
        self._apply_filters()

    def _on_search_text(self, instance, value):
        self._apply_filters()

    def _on_active_toggle(self, instance):
        self._apply_filters()

    def get_selected_index(self):
        lm = self.plant_list.layout_manager
        if not lm or not lm.selected_nodes:
            return None
        return lm.selected_nodes[0]
    
    def get_selected_plant(self):
        idx = self.get_selected_index()
        if idx is None:
            return None
        return self.plant_list.data[idx]   
         
    def on_view_selected(self, instance):
        plant = self.get_selected_plant()
        if plant is None:
            print("No plant selected")
            return
        print("Selected plant:", plant)
    
    def on_delete_selected(self, *args):
        idx = self.get_selected_index()
        if idx is None:
            print("No plant selected to delete")
            return

        selected = self.plant_list.data[idx]
        plant_id = selected.get("id")

        app = App.get_running_app()
        garden_id = getattr(app, 'current_garden_id', None)

        if plant_id and garden_id:
            remove_plant_from_garden(garden_id, plant_id)

        # delete from RecycleView
        self.plant_list.data.pop(idx)

        # clear selection in layout manager
        lm = self.plant_list.layout_manager
        if lm and idx in lm.selected_nodes:
            lm.deselect_node(idx)

        app.screen.current = "garden_view"

    def on_details_button(self, *args):
        plant = self.get_selected_plant()  
        if not plant:
            return

        app = App.get_running_app()
        app.previous_screen = app.screen.current
        details_screen = app.screen.get_screen("plant_details") 
        details_screen.set_plant(plant)
        app.screen.current = "plant_details"