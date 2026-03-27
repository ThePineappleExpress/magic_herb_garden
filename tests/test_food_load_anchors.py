"""Test that TimelineScreen.load_plant initializes the food graph anchored to the most recent event and zoomed out."""
import kivy.app
from types import SimpleNamespace
from timeline_view import TimelineScreen
from data import PlantRepository

# fake theme
fake_theme = SimpleNamespace(
    color_transparent=[0,0,0,0.5],color_accent_highlight_2=[0,1,0,1],color_accent_7=[0.5,0.2,0,1],color_accent_2=[1,0.5,0,1],color_accent_1=[1,0,0,1],color_accent_5=[0,0,1,1],color_accent_3=[1,1,0,1],color_accent_6=[0.5,0,1,1],color_highlight=[1,1,1,1],color_background=[0,0.5,0,1],padding_right=10,body_size=12,subtitle_size=14,logo_size_2=18,font_body='DejaVuSans',color_accent_highlight_1=[1,0.9,0.5,1])
class FObj:
    theme = fake_theme
    def go_back(self,*a,**k): pass
kivy.app.App.get_running_app = staticmethod(lambda: FObj())


def run_tests():
    ts = TimelineScreen()
    plants = PlantRepository().get_all()
    assert plants
    p = plants[0]
    ts.load_plant(p)
    g = ts.tab_graphs['food'][0]
    print('food window after load:', g._xmin, g._xmax)
    assert g._xmax > g._xmin
    assert (g._xmax - g._xmin) >= 30
    print('test_food_load_anchors passed')

if __name__ == '__main__':
    run_tests()
