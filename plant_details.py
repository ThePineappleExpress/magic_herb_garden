import datetime
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock

from helpers import get_difference_days
from storage import load_plant_events
from labels import TitleLabel, FieldLabel, HintLabel, ListTitleLabel, LogoLabel2
from boxes import WrapperBox, WrapperBox, ContentBox, SpacerBox, RedBox, YellowBox, GreenBox, EventBox, SelectableBoxLayout, SelectableEventBox
from buttons import ButtonRed, ButtonGreen, ButtonYellow
from text_inputs import NumTextInput, MedTextInput, LargeTextInput

class EventListView(RecycleView):
    genes = StringProperty("")
    genes_icon = StringProperty("")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.viewclass = "PlantListItem"  # uses the kv rule above
        self.data = []                    # will fill from GardenViewScreen


class PlantDetailsScreen(Screen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plant = None
        self._selected_event_item = None
        app = App.get_running_app()

        # build UI 
        detail_view = WrapperBox(orientation="horizontal")
        spacer_left = SpacerBox(size_hint_x=0.2)
        stripes_holder = WrapperBox(orientation="horizontal")
        stripe_0 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_0)
        stripe_1 = RedBox(); stripes_holder.add_widget(stripe_1)
        stripe_2 = YellowBox(); stripes_holder.add_widget(stripe_2)
        stripe_3 = GreenBox(); stripes_holder.add_widget(stripe_3)
        stripe_4 = ContentBox(size_hint_x=0.45); stripes_holder.add_widget(stripe_4)
        spacer_left.add_widget(stripes_holder)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        title = TitleLabel(text=f"Just look at this [color={TitleLabel().hex_color}]BEAUTY[/color]")
        spacer_left.add_widget(title)
        spacer_vertical = SpacerBox(size_hint_x=0.3)
        spacer_left.add_widget(spacer_vertical)
        detail_view.add_widget(spacer_left)


        content_wrapper = WrapperBox(orientation="vertical", size_hint=(1, 1))

        spacer_box = SpacerBox(size_hint_y=0.1)
        content_wrapper.add_widget(spacer_box)

        header = WrapperBox(orientation="horizontal", size_hint_y=0.3)
        content_wrapper.add_widget(header)

        title_box = ContentBox(orientation="vertical")
        header.add_widget(title_box)
        spacer_box = SpacerBox(size_hint_y=0.2)
        title_box.add_widget(spacer_box)
        
        name_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        self.name_label = FieldLabel(text="", valign="middle", halign="left")
        self.name_label.font_size = app.theme.subtitle_size
        self.name_label.color = app.theme.off_white
        name_box.add_widget(self.name_label)
        title_box.add_widget(name_box)

        strain_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        self.strain_label = FieldLabel(text="", valign="middle", halign="left")
        self.strain_label.font_size = app.theme.logo_size_2
        self.strain_label.color = app.theme.off_white

        strain_box.add_widget(self.strain_label)
        title_box.add_widget(strain_box)

        notes_box = ContentBox(orientation="horizontal", size_hint_y=0.15)
        self.notes_label = FieldLabel(text="", valign="middle", halign="left")
        self.notes_label.font_size = app.theme.body_size
        self.notes_label.color = app.theme.off_white

        notes_box.add_widget(self.notes_label)
        title_box.add_widget(notes_box)

        water_data_box = ContentBox(orientation="horizontal", size_hint_y=0.15)
        self.last_water_label = FieldLabel(text="", valign="middle", halign="left")
        self.last_water_label.font_size = app.theme.body_size
        
        water_data_box.add_widget(self.last_water_label)
        title_box.add_widget(water_data_box)

        spacer = SpacerBox(size_hint_x=0.1)
        header.add_widget(spacer)
        days_passed_box = ContentBox(orientation="vertical", size_hint_x=0.2)
        header.add_widget(days_passed_box)
        
        spacer_box = SpacerBox(size_hint_y=0.3)
        days_passed_box.add_widget(spacer_box)

        days_passed_title_box = ContentBox(orientation="horizontal", size_hint_y=0.2)
        days_passed_box.add_widget(days_passed_title_box)
        days_passed_title = FieldLabel(text="Day", valign="middle", halign="right")
        days_passed_title.font_size = app.theme.subtitle_size        
        days_passed_title_box.add_widget(days_passed_title)

        days_passed_value_box = ContentBox(orientation="horizontal", size_hint_y=0.5)
        days_passed_box.add_widget(days_passed_value_box)
        self.days_passed_value = FieldLabel(text="", valign="middle", halign="right")
        self.days_passed_value.font_size = app.theme.logo_size_1
        self.days_passed_value.color = app.theme.off_white
        days_passed_value_box.add_widget(self.days_passed_value)

        days_stage_box = ContentBox(orientation="vertical", size_hint_y=0.1)
        days_passed_box.add_widget(days_stage_box)
        self.days_stage_value = FieldLabel(text="", valign="middle", halign="right")
        self.days_stage_value.font_size = app.theme.body_size
        self.days_stage_value.color = app.theme.off_white
        days_stage_box.add_widget(self.days_stage_value)



        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        self.info_box = WrapperBox(orientation="vertical", size_hint_x=1, size_hint_y=0.8)

        content_wrapper.add_widget(self.info_box)

        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)

        # events scroll 
        scroll_events = ContentBox(orientation="vertical", size_hint_y=0.2, size_hint_x=1)
        self.events_scroll = ScrollView(do_scroll_x=True, do_scroll_y=False,)

        self.events_container = WrapperBox(orientation="horizontal", size_hint_x=None, size_hint_y=1, padding=5, spacing=0,)
        self.events_container.bind(minimum_width=self.events_container.setter("width"))
        self.events_scroll.add_widget(self.events_container)
        scroll_events.add_widget(self.events_scroll)
        content_wrapper.add_widget(scroll_events)
        spacer_box = SpacerBox(size_hint_y=0.02)
        content_wrapper.add_widget(spacer_box)


        buttons = ContentBox(size_hint_y=0.1)
        go_back_btn = ButtonRed(text="Back")
        go_back_btn.bind(on_press=App.get_running_app().go_back)
        buttons.add_widget(go_back_btn)
        content_wrapper.add_widget(buttons)

        detail_view.add_widget(content_wrapper)
        spacer_right = SpacerBox(size_hint_x=0.1)
        detail_view.add_widget(spacer_right)
        self.add_widget(detail_view)

        # load and show events
        self._load_and_display_events()

    def set_plant(self, plant: dict):
        self.plant = plant or {}
        self._update_ui()

    def _update_ui(self):
        app = App.get_running_app()
        plant = self.plant or {}
        self.genes = plant.get("genes", "")
        self.name_label.text = " | ".join([plant.get("name", ""), self.genes])
        
        self.strain_label.text = plant.get("strain", "")
        genes = (self.genes or "").strip().lower()
        if genes == "sativa":
            self.strain_label.color = app.theme.light_green
        elif genes == "indica":
            self.strain_label.color = app.theme.nice_green
        elif genes == "hybrid":
            self.strain_label.color = app.theme.light_yellow
        else:
            self.strain_label.color = app.theme.off_white
        self.notes_label.text = plant.get("notes")
        days_passed = get_difference_days(datetime.datetime.now(), plant.get("date_planted", ""))
        self.days_passed_value.text = str(days_passed) if days_passed is not None else "–"
        self._load_and_display_events()

    def _select_event_item(self, item, event):
        if self._selected_event_item and self._selected_event_item != item:
            self._selected_event_item.selected = False
        item.selected = True
        self._selected_event_item = item
        self._selected_event_data = event 
        self.selected_event_view()


    def _load_and_display_events(self):
        self.events_container.clear_widgets()
        self._selected_event_item = None

        plant = self.plant or {}
        plant_id = plant.get("id")
        if not plant_id:
            return

        data = load_plant_events(str(plant_id))
        if not data:
            return
        events = data.get("events", [])
        if not events:
            return

        def _parse_ts(value):
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return datetime.datetime.fromtimestamp(value)
            if isinstance(value, str):
                return datetime.datetime.fromisoformat(value)
            return None

        def _sort_key(event):
            ts_value = event.get("ts") if isinstance(event, dict) else None
            parsed = _parse_ts(ts_value)
            if parsed:
                return (0, parsed)
            return (1, str(ts_value))

        # chronological (oldest -> newest)
        events_sorted = sorted(events, key=_sort_key)

        event_boxes = []

        for event in events_sorted:
            event_type = event.get("type", "")
            feeding = event.get("feeding", "")
            ts = event.get("ts", "")
            days_ago = get_difference_days(datetime.datetime.now(), ts)

            # selectable event item
            box = SelectableEventBox(orientation="horizontal", size_hint=(None, 1), width=200)
            box.bind(on_release=lambda _btn, _event=event, _item=box: self._select_event_item(_item, _event))

            event_boxes.append((box, event))  # Track box and event

            info_box = EventBox(orientation='vertical', padding=App.get_running_app().theme.padding_right)
            box.add_widget(info_box)
            
            if days_ago == 0:
                info_box.add_widget(HintLabel(text="Today", font_size="12sp", valign="bottom"))
            elif days_ago == 1:
                info_box.add_widget(HintLabel(text="Yesterday", font_size="12sp", valign="bottom"))
            elif days_ago > 1 and days_ago < 7:
                info_box.add_widget(HintLabel(text=f"{days_ago} days ago", font_size="12sp", valign="bottom"))
            elif days_ago >= 7 and days_ago < 30:
                weeks = days_ago // 7
                if days_ago < 14:
                    s = ""
                else:
                    s = "s"
                info_box.add_widget(HintLabel(text=f"{weeks} week{s} ago", font_size="12sp", valign="bottom"))
            elif days_ago >= 30 and days_ago < 365:
                months = days_ago // 30
                if days_ago < 60:
                    s = ""
                else:
                    s = "s"
                info_box.add_widget(HintLabel(text=f"{months} month{s} ago", font_size="12sp", valign="bottom"))
            elif days_ago >= 365:
                years = days_ago // 365
                if days_ago < 730:
                    s = ""
                else:
                    s = "s"
                info_box.add_widget(HintLabel(text=f"{years} year{s} ago", font_size="12sp", valign="bottom"))
            else:
                info_box.add_widget(SpacerBox())
            
            
            
            info_box.add_widget(SpacerBox())
            info_box.add_widget(HintLabel(text=str(event_type), font_size="12sp", valign="top"))
            
            color_bar = ContentBox(orientation="vertical", size_hint_x=0.005)
            color_bar.add_widget(RedBox())
            color_bar.add_widget(YellowBox())
            color_bar.add_widget(GreenBox())
            box.add_widget(color_bar)
            self.events_container.add_widget(box)

        # last event summary 
        last = events_sorted[-1]
        if last.get("type") == "watering":
            vol = last.get("volume_l")
            ph = last.get("ph")
            ppm = last.get("ppm")
            ts = last.get("ts")
            self.last_water_label.text = f"Last water: {vol} L, pH {ph}, {ppm} ppm @ {ts}"
        else:
            self.last_water_label.text = f"Last event: {last.get('type')} @ {last.get('ts')}"

        Clock.schedule_once(lambda *_: setattr(self.events_scroll, "scroll_x", 1), 0)
        if event_boxes:
            last_box, last_event = event_boxes[-1]
            Clock.schedule_once(lambda *_: self._select_event_item(last_box, last_event), 0)

    def selected_event_view(self):
        self.info_box.clear_widgets()
        app = App.get_running_app()
        plant = self.plant or {}
        event = getattr(self, '_selected_event_data', None) 
        if not event:
            return
        event_date = event.get("ts", "")
        formatter = []
        split_date = event_date.split("-")
        self.days_passed = get_difference_days(event.get("ts", ""), plant.get("date_planted", ""))
        self.days_passed_value.text = str(self.days_passed) if self.days_passed is not None else "–"
        for i in split_date[::-1]:
            formatter.append(i)
        formatted_date = " ".join(formatter)
        event_type = event.get("type", "")
        notes = event.get("notes", "")
        water_volume = event.get("volume_l", "")
        water_temperature = event.get("water_temp_c", "")
        ph = event.get("ph", "")
        ppm = event.get("ppm", "")

        if event.get("type") == "feeding" :
            feeding = event.get("feeding", "")
            grow_mix = float(feeding.get("grow_mix", ""))
            root_mix = float(feeding.get("root_mix", ""))
            bloom_mix = float(feeding.get("bloom_mix", ""))
            bloom_boost = float(feeding.get("bloom_boost", ""))
            soil_boost = float(feeding.get("soil_boost", ""))
            vit_boost = float(feeding.get("vit_boost", ""))
            CalMag = float(feeding.get("CalMag", ""))
            myco_trico = bool(feeding.get("myco_trico", ""))

        plant = event.get("plant", "")
        stage = plant.get("stage", "")
        health = plant.get("health", "")
        plant_height = int(plant.get("plant_height", ""))
        number_of_nodes = int(plant.get("num_nodes", ""))
        node_spacing = float(plant.get("node_spacing", ""))
        main_stems = int(plant.get("main_stem_number", ""))
        coloration = plant.get("leaf_color", "")
        morphology = plant.get("leaf_morphology", "")
        deficiencies = plant.get("deficiencies", "")
        def_nitrogen = deficiencies.get("n","")
        def_phosphorus = deficiencies.get("p","")
        def_potassium = deficiencies.get("k","")
        def_calcium = deficiencies.get("ca","")
        def_magnesium = deficiencies.get("mg","")
        def_sulfur = deficiencies.get("s","")
        def_iron = deficiencies.get("fe","")
        def_manganese = deficiencies.get("mn","")
        def_zinc = deficiencies.get("zn","")
        def_copper = deficiencies.get("cu","")
        def_boron = deficiencies.get("b","") 
        def_molybdenum = deficiencies.get("mo","")
        excess = plant.get("excess", "")
        exc_nitrogen = excess.get("n","")
        exc_phosphorus = excess.get("p","")
        exc_potassium = excess.get("k","")
        exc_calcium = excess.get("ca","")
        exc_magnesium = excess.get("mg","")
        exc_sulfur = excess.get("s","")
        exc_iron = excess.get("fe","")
        exc_manganese = excess.get("mn","")
        exc_zinc = excess.get("zn","")
        exc_copper = excess.get("cu","")
        exc_boron = excess.get("b","") 
        exc_molybdenum = excess.get("mo","")
        days_stage = stage
        self.days_stage_value.text = f"{days_stage}" if days_stage is not None else "–"

        environment = event.get("environment", "")
        soil_moisture = environment.get("soil_moisture", "")
        air_temperature = int(environment.get("air_temp_c",""))
        soil_ph = float(environment.get("soil_ph",""))
        humidity = int(environment.get("rh_percent",""))
        vpd = float(environment.get("vpd_kpa",""))
        light_schedule = environment.get("light_schedule","")
        ppfd = int(environment.get("ppfd",""))

        event_details = WrapperBox(orientation="vertical")

        event_title_row = WrapperBox(orientation="horizontal", size_hint_y=0.25)
        event_details.add_widget(event_title_row)

        date_and_type_box = WrapperBox(orientation="vertical", size_hint_x=0.3)
        event_title_row.add_widget(date_and_type_box)

        event_date_label_box =  ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(event_date_label_box)
        event_date_value = FieldLabel(text=f"{formatted_date}", valign="bottom", halign="left")
        event_date_value.color = app.theme.off_white
        event_date_value.font_size = app.theme.title_size
        event_date_label_box.add_widget(event_date_value)

        event_type_label_box = ContentBox(orientation="horizontal")
        date_and_type_box.add_widget(event_type_label_box)
        event_type_label = FieldLabel(text=f"{event_type}", valign="top", halign="left")
        if event_type == "water":
            event_type_label.color = app.theme.nice_blue
        elif event_type == "feeding":
            event_type_label.color = app.theme.nice_yellow
        else:
            event_type_label.color = app.theme.nice_green
        event_type_label.font_size = app.theme.subtitle_size
        event_type_label_box.add_widget(event_type_label)
        
        environment_box = WrapperBox(orientation="horizontal")         
        event_title_row.add_widget(environment_box)

        temperature_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(temperature_box)

        temperature_title_box = ContentBox(orientation="horizontal")
        temperature_box.add_widget(temperature_title_box)
        temperature_label_title = FieldLabel(text="Air Temp", valign="bottom", halign="left")
        temperature_label_title.color = app.theme.nice_green
        temperature_label_title.font_size = app.theme.small_size
        temperature_title_box.add_widget(temperature_label_title)

        temperature_label_box = ContentBox(orientation="horizontal")
        temperature_box.add_widget(temperature_label_box)
        temperature_label = FieldLabel(text=f"{air_temperature}°C", valign="top", halign="left")
        temperature_label.font_size = app.theme.subtitle_size
        temperature_label.color = app.theme.off_white
        temperature_label_box.add_widget(temperature_label)

        humidity_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(humidity_box)
        
        humidity_title_box = ContentBox(orientation="horizontal")
        humidity_box.add_widget(humidity_title_box)
        humidity_title = FieldLabel(text="Humidity", valign="bottom", halign="left")
        humidity_title.color = app.theme.nice_green
        humidity_title.font_size = app.theme.small_size
        humidity_title_box.add_widget(humidity_title)

        humidity_value_box = ContentBox(orientation="horizontal")
        humidity_box.add_widget(humidity_value_box)
        humidity_value = FieldLabel(text=f"{humidity} %", valign="top", halign="left")
        humidity_value.font_size = app.theme.subtitle_size
        humidity_value.color = app.theme.off_white
        humidity_value_box.add_widget(humidity_value)
        vpd_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(vpd_box)

        vpd_title_box = ContentBox(orientation="horizontal")
        vpd_box.add_widget(vpd_title_box)
        vpd_title = FieldLabel(text="VPD", valign="bottom", halign="left")
        vpd_title.color = app.theme.nice_green
        vpd_title.font_size = app.theme.small_size
        vpd_title_box.add_widget(vpd_title)

        vpd_value_box = ContentBox(orientation="horizontal")
        vpd_box.add_widget(vpd_value_box)
        vpd_value = FieldLabel(text=f"{vpd} kPa", valign="top", halign="left")
        vpd_value.font_size = app.theme.subtitle_size
        vpd_value.color = app.theme.off_white
        vpd_value_box.add_widget(vpd_value)

        soil_ph_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(soil_ph_box)

        soil_ph_title_box = ContentBox(orientation="horizontal")
        soil_ph_box.add_widget(soil_ph_title_box)
        soil_ph_title = FieldLabel(text="Soil pH", valign="bottom", halign="left")
        soil_ph_title.color = app.theme.nice_green
        soil_ph_title.font_size = app.theme.small_size
        soil_ph_title_box.add_widget(soil_ph_title)

        soil_ph_value_box = ContentBox(orientation="horizontal")
        soil_ph_box.add_widget(soil_ph_value_box)
        soil_ph_value = FieldLabel(text=f"{soil_ph}", valign="top", halign="left")
        soil_ph_value.font_size = app.theme.subtitle_size
        soil_ph_value.color = app.theme.off_white
        soil_ph_value_box.add_widget(soil_ph_value)

        soil_moisture_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(soil_moisture_box)

        soil_moisture_title_box = ContentBox(orientation="horizontal")
        soil_moisture_box.add_widget(soil_moisture_title_box)
        soil_moisture_title = FieldLabel(text="Soil", valign="bottom", halign="left")
        soil_moisture_title.color = app.theme.nice_green
        soil_moisture_title.font_size = app.theme.small_size
        soil_moisture_title_box.add_widget(soil_moisture_title)

        soil_moisture_value_box = ContentBox(orientation="horizontal")
        soil_moisture_box.add_widget(soil_moisture_value_box)
        soil_moisture_value = FieldLabel(text=f"{soil_moisture}", valign="top", halign="left")
        soil_moisture_value.font_size = app.theme.subtitle_size
        soil_moisture_value.color = app.theme.off_white
        soil_moisture_value_box.add_widget(soil_moisture_value)

        ppfd_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(ppfd_box)

        ppfd_title_box = ContentBox(orientation="horizontal")
        ppfd_box.add_widget(ppfd_title_box)
        ppfd_title = FieldLabel(text="PPFD", valign="bottom", halign="left")
        ppfd_title.color = app.theme.nice_green
        ppfd_title.font_size = app.theme.small_size
        ppfd_title_box.add_widget(ppfd_title)

        ppfd_value_box = ContentBox(orientation="horizontal")
        ppfd_box.add_widget(ppfd_value_box)
        ppfd_value = FieldLabel(text=f"{ppfd} µmol/m²/s", valign="top", halign="left")
        ppfd_value.font_size = app.theme.subtitle_size
        ppfd_value.color = app.theme.off_white
        ppfd_value_box.add_widget(ppfd_value)

        light_cycle_box = WrapperBox(orientation="vertical")
        environment_box.add_widget(light_cycle_box)

        light_cycle_title_box = ContentBox(orientation="horizontal")
        light_cycle_box.add_widget(light_cycle_title_box)
        light_cycle_title = FieldLabel(text="Light", valign="bottom", halign="left")
        light_cycle_title.color = app.theme.nice_green
        light_cycle_title.font_size = app.theme.small_size
        light_cycle_title_box.add_widget(light_cycle_title)

        light_cycle_value_box = ContentBox(orientation="horizontal")
        light_cycle_box.add_widget(light_cycle_value_box)
        light_cycle_value = FieldLabel(text=f"{"/".join(map(str, light_schedule))}", valign="top", halign="left")
        light_cycle_value.font_size = app.theme.subtitle_size
        light_cycle_value.color = app.theme.off_white
        light_cycle_value_box.add_widget(light_cycle_value)

        main_data_column = WrapperBox(orientation="horizontal")
        event_details.add_widget(main_data_column)

        water_and_food_box = WrapperBox(orientation="vertical", size_hint_x=0.4)
        main_data_column.add_widget(water_and_food_box)

        water_row = WrapperBox(orientation="horizontal", size_hint_y=0.2)
        water_and_food_box.add_widget(water_row)

        if event_type == "watering" or event_type == "feeding":

            water_data_box = WrapperBox(orientation="horizontal")
            water_row.add_widget(water_data_box)

            water_volume_box = WrapperBox(orientation="vertical")
            water_data_box.add_widget(water_volume_box)

            water_volume_title_box = ContentBox(orientation="horizontal")
            water_volume_box.add_widget(water_volume_title_box)
            water_volume_title = FieldLabel(text="Ltr", valign="bottom", halign="left")
            water_volume_title.color = app.theme.nice_blue
            water_volume_title.font_size = app.theme.small_size
            water_volume_title_box.add_widget(water_volume_title)

            water_volume_value_box = ContentBox(orientation="horizontal")
            water_volume_box.add_widget(water_volume_value_box)
            water_volume_value = FieldLabel(text=f"{water_volume}", valign="top", halign="left")
            water_volume_value.font_size = app.theme.subtitle_size
            water_volume_value.color = app.theme.off_white
            water_volume_value_box.add_widget(water_volume_value)

            water_temperature_box = WrapperBox(orientation="vertical")
            water_data_box.add_widget(water_temperature_box)

            water_temperature_title_box = ContentBox(orientation="horizontal")
            water_temperature_box.add_widget(water_temperature_title_box)
            water_temperature_title = FieldLabel(text="Temp", valign="bottom", halign="left")
            water_temperature_title.color = app.theme.nice_blue
            water_temperature_title.font_size = app.theme.small_size
            water_temperature_title_box.add_widget(water_temperature_title)

            water_temperature_value_box = ContentBox(orientation="horizontal")
            water_temperature_box.add_widget(water_temperature_value_box)
            water_temperature_value = FieldLabel(text=f"{water_temperature}°C", valign="top", halign="left")
            water_temperature_value.font_size = app.theme.subtitle_size
            water_temperature_value.color = app.theme.off_white
            water_temperature_value_box.add_widget(water_temperature_value)

            ph_box = WrapperBox(orientation="vertical")
            water_data_box.add_widget(ph_box)

            ph_title_box = ContentBox(orientation="horizontal")
            ph_box.add_widget(ph_title_box)
            ph_title = FieldLabel(text="pH", valign="bottom", halign="left")
            ph_title.color = app.theme.nice_blue
            ph_title.font_size = app.theme.small_size
            ph_title_box.add_widget(ph_title)

            ph_value_box = ContentBox(orientation="horizontal")
            ph_box.add_widget(ph_value_box)
            ph_value = FieldLabel(text=f"{ph}", valign="top", halign="left")
            ph_value.font_size = app.theme.subtitle_size
            ph_value.color = app.theme.off_white
            ph_value_box.add_widget(ph_value)

            ppm_box = WrapperBox(orientation="vertical")
            water_data_box.add_widget(ppm_box)

            ppm_title_box = ContentBox(orientation="horizontal")
            ppm_box.add_widget(ppm_title_box)
            ppm_title = FieldLabel(text="PPM", valign="bottom", halign="left")
            ppm_title.color = app.theme.nice_blue
            ppm_title.font_size = app.theme.small_size
            ppm_title_box.add_widget(ppm_title) 

            ppm_value_box = ContentBox(orientation="horizontal")
            ppm_box.add_widget(ppm_value_box)
            ppm_value = FieldLabel(text=f"{ppm}", valign="top", halign="left")
            ppm_value.font_size = app.theme.subtitle_size
            ppm_value.color = app.theme.off_white
            ppm_value_box.add_widget(ppm_value)
            
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)


        if event_type == "feeding":
            feeding_row_1 = WrapperBox(orientation="horizontal", size_hint_y=0.2)
            water_and_food_box.add_widget(feeding_row_1)
            feeding_box = WrapperBox(orientation="horizontal")
            feeding_row_1.add_widget(feeding_box)

            grow_box = WrapperBox(orientation="vertical")
            feeding_box.add_widget(grow_box)

            if stage == "vegetative":
                grow_title_box = ContentBox(orientation="horizontal")
                grow_box.add_widget(grow_title_box)
                grow_title = FieldLabel(text="Veg", valign="bottom", halign="left")
                grow_title.color = app.theme.nice_yellow
                grow_title.font_size = app.theme.small_size
                grow_title_box.add_widget(grow_title)

                grow_value_box = ContentBox(orientation="horizontal")
                grow_box.add_widget(grow_value_box)
                grow_value = FieldLabel(text=f"{grow_mix}", valign="top", halign="left")
                grow_value.font_size = app.theme.subtitle_size
                grow_value.color = app.theme.off_white
                grow_value_box.add_widget(grow_value)
            else:
                spacer = SpacerBox(size_hint_y=0.2)
                grow_box.add_widget(spacer)
            

            root_box = WrapperBox(orientation="vertical")
            feeding_box.add_widget(root_box)

            root_title_box = ContentBox(orientation="horizontal")
            root_box.add_widget(root_title_box)
            root_title = FieldLabel(text="Root", valign="bottom", halign="left")
            root_title.color = app.theme.nice_yellow
            root_title.font_size = app.theme.small_size
            root_title_box.add_widget(root_title)

            root_value_box = ContentBox(orientation="horizontal")
            root_box.add_widget(root_value_box)
            root_value = FieldLabel(text=f"{root_mix}", valign="top", halign="left")
            root_value.font_size = app.theme.subtitle_size
            root_value.color = app.theme.off_white
            root_value_box.add_widget(root_value)

            soil_boost_box = WrapperBox(orientation="vertical")
            feeding_box.add_widget(soil_boost_box)

            soil_boost_title_box = ContentBox(orientation="horizontal")
            soil_boost_box.add_widget(soil_boost_title_box)
            soil_boost_title = FieldLabel(text="Soil", valign="bottom", halign="left")
            soil_boost_title.color = app.theme.nice_yellow
            soil_boost_title.font_size = app.theme.small_size
            soil_boost_title_box.add_widget(soil_boost_title)

            soil_boost_value_box = ContentBox(orientation="horizontal")
            soil_boost_box.add_widget(soil_boost_value_box)
            soil_boost_value = FieldLabel(text=f"{soil_boost}", valign="top", halign="left")
            soil_boost_value.font_size = app.theme.subtitle_size
            soil_boost_value.color = app.theme.off_white
            soil_boost_value_box.add_widget(soil_boost_value)
            
            vit_box = WrapperBox(orientation="vertical")
            feeding_box.add_widget(vit_box)

            vit_title_box = ContentBox(orientation="horizontal")
            vit_box.add_widget(vit_title_box)
            vit_title = FieldLabel(text="Vit", valign="bottom", halign="left")
            vit_title.color = app.theme.nice_yellow
            vit_title.font_size = app.theme.small_size
            vit_title_box.add_widget(vit_title)

            vit_value_box = ContentBox(orientation="horizontal")
            vit_box.add_widget(vit_value_box)
            vit_value = FieldLabel(text=f"{vit_boost}", valign="top", halign="left")
            vit_value.font_size = app.theme.subtitle_size
            vit_value.color = app.theme.off_white
            vit_value_box.add_widget(vit_value)
            
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)


        if event_type == "feeding":
            feeding_row_2 = WrapperBox(orientation="horizontal", size_hint_y=0.2)
            water_and_food_box.add_widget(feeding_row_2)            
            feeding_box_2 = WrapperBox(orientation="horizontal")
            feeding_row_2.add_widget(feeding_box_2)
            
            if stage == "flowering":
                bloom_box = WrapperBox(orientation="vertical")
                feeding_box_2.add_widget(bloom_box)

                bloom_title_box = ContentBox(orientation="horizontal")
                bloom_box.add_widget(bloom_title_box)
                bloom_title = FieldLabel(text="Flower", valign="bottom", halign="left")
                bloom_title.color = app.theme.nice_yellow
                bloom_title.font_size = app.theme.small_size
                bloom_title_box.add_widget(bloom_title)

                bloom_value_box = ContentBox(orientation="horizontal")
                bloom_box.add_widget(bloom_value_box)
                bloom_value = FieldLabel(text=f"{bloom_mix}", valign="top", halign="left")
                bloom_value.font_size = app.theme.subtitle_size
                bloom_value.color = app.theme.off_white
                bloom_value_box.add_widget(bloom_value)
            else:
                spacer = SpacerBox()
                feeding_box_2.add_widget(spacer)

            if stage == "flowering":
                bloom_boost_box = WrapperBox(orientation="vertical")
                feeding_box_2.add_widget(bloom_boost_box)

                bloom_boost_title_box = ContentBox(orientation="horizontal")
                bloom_boost_box.add_widget(bloom_boost_title_box)
                bloom_boost_title = FieldLabel(text="Tops", valign="bottom", halign="left")
                bloom_boost_title.color = app.theme.nice_yellow
                bloom_boost_title.font_size = app.theme.small_size
                bloom_boost_title_box.add_widget(bloom_boost_title)

                bloom_boost_value_box = ContentBox(orientation="horizontal")
                bloom_boost_box.add_widget(bloom_boost_value_box)
                bloom_boost_value = FieldLabel(text=f"{bloom_boost}ml", valign="top", halign="left")
                bloom_boost_value.font_size = app.theme.subtitle_size
                bloom_boost_value.color = app.theme.off_white
                bloom_boost_value_box.add_widget(bloom_boost_value)
            else:
                spacer = SpacerBox()
                feeding_box_2.add_widget(spacer)

            calmag_box = WrapperBox(orientation="vertical")
            feeding_box_2.add_widget(calmag_box) 

            calmag_title_box = ContentBox(orientation="horizontal")
            calmag_box.add_widget(calmag_title_box)
            calmag_title = FieldLabel(text="CalMag", valign="bottom", halign="left")
            calmag_title.color = app.theme.nice_yellow
            calmag_title.font_size = app.theme.small_size
            calmag_title_box.add_widget(calmag_title)

            calmag_value_box = ContentBox(orientation="horizontal")
            calmag_box.add_widget(calmag_value_box)
            calmag_value = FieldLabel(text=f"{CalMag}ml", valign="top", halign="left")
            calmag_value.font_size = app.theme.subtitle_size
            calmag_value.color = app.theme.off_white
            calmag_value_box.add_widget(calmag_value)

            myco_trico_box = WrapperBox(orientation="vertical")
            feeding_box_2.add_widget(myco_trico_box)

            myco_trico_title_box = ContentBox(orientation="horizontal")
            myco_trico_box.add_widget(myco_trico_title_box)
            myco_trico_title = FieldLabel(text="Fungi", valign="bottom", halign="left")
            myco_trico_title.color = app.theme.nice_yellow
            myco_trico_title.font_size = app.theme.small_size
            myco_trico_title_box.add_widget(myco_trico_title)

            myco_trico_value_box = ContentBox(orientation="horizontal")
            myco_trico_box.add_widget(myco_trico_value_box)
            myco_trico_value = FieldLabel(text=f"{'Yes' if myco_trico else 'No'}", valign="top", halign="left")
            myco_trico_value.font_size = app.theme.subtitle_size
            myco_trico_value.color = app.theme.nice_green if myco_trico else app.theme.light_green
            myco_trico_value_box.add_widget(myco_trico_value)
            
        else:
            spacer = SpacerBox(size_hint_y=0.2)
            water_and_food_box.add_widget(spacer)




        notes_box = WrapperBox(orientation="vertical", size_hint_x = 0.6)
        main_data_column.add_widget(notes_box)

        notes_title_box = ContentBox(orientation="horizontal", size_hint_y=0.3)
        notes_box.add_widget(notes_title_box)
        notes_title = FieldLabel(text="Notes", valign="bottom", halign="left")
        notes_title.color = app.theme.nice_green
        notes_title.font_size = app.theme.subtitle_size
        notes_title_box.add_widget(notes_title)
        
        notes_text_box = ContentBox(orientation="horizontal", size_hint_y=0.7)
        notes_box.add_widget(notes_text_box)
        notes_text = FieldLabel(text=f"{notes}", valign="top", halign="left")
        notes_text.font_size = app.theme.small_size
        notes_text.color = app.theme.off_white
        notes_text_box.add_widget(notes_text)



        
        self.info_box.add_widget(event_details)



        

