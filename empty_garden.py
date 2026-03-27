from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from helpers import go_to_add_garden
from labels import LogoLabel1, LogoLabel2, LogoLabel3
from buttons import ButtonGreen, ButtonYellow
from boxes import WrapperBox, ContentBox, ItemBox, TitleBox, RedBox, YellowBox, GreenBox
from screens import BaseScreen

class EmptyGardenScreen(BaseScreen):
    theme = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # build layout directly on this Screen
        first_launch = WrapperBox(orientation="vertical")
        spacer = WrapperBox(size_hint_y=0.2)
        first_launch.add_widget(spacer)

        layout = ContentBox( orientation="vertical", size_hint_x=0.6, pos_hint={"center_x": 0.5, "center_y": 0.5})

        title_bar = TitleBox(orientation="horizontal")
        layout_holder = ContentBox(orientation="horizontal")

        stripes_holder = ContentBox(orientation="horizontal", size_hint_x=0.2, spacing=0)
        stripe_1 = RedBox(size_hint_x=0.33)
        stripe_2 = YellowBox(size_hint_x=0.34)
        stripe_3 = GreenBox(size_hint_x=0.33)
        stripes_holder.add_widget(stripe_1)
        stripes_holder.add_widget(stripe_2)
        stripes_holder.add_widget(stripe_3)

        layout_holder.add_widget(stripes_holder)

        logo_holder = ItemBox(orientation="vertical", spacing=0)
        label_1 = LogoLabel2(text="Magic")
        label_2 = LogoLabel1(text="HERB GARDEN")
        label_3 = LogoLabel3(text="Ultimate grow tracker")
        logo_holder.add_widget(label_1)
        logo_holder.add_widget(label_2)
        logo_holder.add_widget(label_3)

        plant_button = ItemBox(orientation="vertical", size_hint_y=0.5)
        plant_seed = ButtonGreen(text="Plant something beautiful")
        plant_seed.bind(on_press=go_to_add_garden)
        plant_button.add_widget(plant_seed)
        logo_holder.add_widget(plant_button)

        layout_holder.add_widget(logo_holder)
        title_bar.add_widget(layout_holder)

        layout.add_widget(title_bar)
        first_launch.add_widget(layout)
        spacer = WrapperBox(size_hint_y=0.2)
        first_launch.add_widget(spacer)

        # add everything to this Screen
        self.add_widget(first_launch)


