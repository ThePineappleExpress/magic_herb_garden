import sys
from datetime import date
from kivy.config import Config
from kivy.factory import Factory
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget
from kivy.graphics.svg import Svg
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale

from labels import TitleLabel
from storage import load_plants, save_plants, load_plant_events
from helpers import on_plant_seed, get_difference_days
from boxes import TitleBox, WrapperBox, ContentBox, ItemBox, SpacerBox, RedBox, YellowBox, GreenBox, SelectableBoxLayout, SelectableRecycleBoxLayout
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import NumTextInput, MedTextInput, LargeTextInput
class LeafIcon(Widget):
    source = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(source=self._redraw, pos=self._redraw, size=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.source:
            return
        svg = Svg(self.source)
        # guard against zero sizes
        svg_w = svg.width or 1
        svg_h = svg.height or 1
        scale = min((self.width / svg_w) * 0.8, (self.height / svg_h) * 0.8)
        # center the icon after scaling
        offset_x = (self.width / scale - svg_w) / 2
        offset_y = (self.height / scale - svg_h) / 2

        # draw with transforms so we don't mutate the Svg instruction
        self.canvas.add(PushMatrix())
        self.canvas.add(Translate(self.x, self.y))
        self.canvas.add(Scale(scale, scale, 1))
        self.canvas.add(Translate(offset_x, offset_y))
        self.canvas.add(svg)
        self.canvas.add(PopMatrix())
class PlantListView(RecycleView):
    genes = StringProperty("")
    genes_icon = StringProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"  # uses the kv rule above
        self.data = []                    # will fill from GardenViewScreen

    def on_genes(self, instance, value):
        if value == "Sativa":
            self.genes_icon = "S"
        elif value == "Indica":
            self.genes_icon = "I"
        elif value == "Hybrid":
            self.genes_icon = "H"
        else:
            self.genes_icon = "?"

class GardenViewScreen(Screen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        garden_view = WrapperBox(orientation="horizontal", size_hint_x=1)
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
        title = TitleLabel(text = f"My magical [color={TitleLabel().hex_color}]GARDEN[/color]")
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        garden_view.add_widget(spacer_left)

        content_wrapper = ContentBox(orientation="vertical", size_hint=(1, 1))

        header = TitleBox(orientation="horizontal", size_hint_y=0.1)
        spacer = SpacerBox(size_hint_x=0.8)
        header.add_widget(spacer)
        side_menu = ItemBox(orientation='horizontal', size_hint_x=0.2)

        exit_btn = Button(text="Exit\nGarden", size_hint_x=0.5)
        exit_btn.bind(on_press=lambda instance: sys.exit(0))
        side_menu.add_widget(exit_btn)

        header.add_widget(side_menu)

        content_wrapper.add_widget(header)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)
        
        garden_list = ItemBox(orientation="horizontal", size_hint_y=1)

        spacer_box = SpacerBox(size_hint_x=0.02)
        garden_list.add_widget(spacer_box)

        self.plant_list = PlantListView(size_hint_x=1)
        garden_list.add_widget(self.plant_list)

        spacer_box = SpacerBox(size_hint_x=0.02)
        garden_list.add_widget(spacer_box)

        content_wrapper.add_widget(garden_list)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        garden_footer = ContentBox(orientation="horizontal", size_hint_y=0.1)
        spacer_box = SpacerBox(size_hint_x=0.8)
        garden_footer.add_widget(spacer_box)
        add_plant_btn = ButtonGreen(text="Add Plant")
        add_plant_btn.bind(on_press=on_plant_seed)
        garden_footer.add_widget(add_plant_btn)
        view_selected_btn = ButtonYellow(text="View Selected Plant")
        view_selected_btn.bind(on_press=self.on_details_button)
        view_selected_btn.bind(on_press=self.on_view_selected)
        garden_footer.add_widget(view_selected_btn)
        delete_selected_btn = ButtonRed(text="Delete Selected Plant")
        delete_selected_btn.bind(on_press=self.on_delete_selected)
        garden_footer.add_widget(delete_selected_btn)

        content_wrapper.add_widget(garden_footer)

        garden_view.add_widget(content_wrapper)

        self.add_widget(garden_view)
        self.refresh_plants()

    def refresh_plants(self):
        plants = load_plants()
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
                last_watering = "–"
            else:
                last_watering = str(last_watering)
            next_watering = "–"
            flower_status = "–"
            harvest_status = "–"

            # example: rough days to flower based on estimate and date_planted
            dt_str = p.get("date_planted")
            base_f = p.get("days_to_flower") 
            est_f = base_f + 14
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
                        harvest_status = f"Harvested!"
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
                        flower_status = f"Flowering!"
                    elif days_left <= 0 and harvest_status == "Harvested!":
                        flower_status = f"Harvested!"
                except Exception:
                    flower_status = f"{est_f}"
            medium = p.get("medium")


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

        self.plant_list.data = data

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

        # identify the plant (e.g. by id)
        selected = self.plant_list.data[idx]
        plant_id = selected.get("id") 

        # 1) delete from storage
        plants = load_plants()
        if plant_id:
            plants = [p for p in plants if isinstance(p, dict) and p.get("id") != plant_id]
        else:
            if 0 <= idx < len(plants):
                plants.pop(idx)
        save_plants(plants)

        # 2) delete from RecycleView
        self.plant_list.data.pop(idx)

        # clear selection in layout manager
        lm = self.plant_list.layout_manager
        if lm and idx in lm.selected_nodes:
            lm.deselect_node(idx)

    def on_details_button(self, *args):
        plant = self.get_selected_plant()  
        if not plant:
            return

        app = App.get_running_app()
        app.previous_screen = app.screen.current
        details_screen = app.screen.get_screen("plant_details") 
        details_screen.set_plant(plant)
        app.screen.current = "plant_details"