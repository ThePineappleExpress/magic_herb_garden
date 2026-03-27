"""Test preserving x-window when toggling relative/absolute in the food tab."""
from types import SimpleNamespace
from timeline_view import TimelineScreen, SimpleGraph
# Provide a fake app theme so SimpleGraph can be instantiated in tests
import kivy.app
fake_theme = SimpleNamespace(
    color_transparent=[0,0,0,0.5],
    color_accent_highlight_2=[0,1,0,1],
    color_accent_7=[0.5,0.2,0,1],
    color_accent_2=[1,0.5,0,1],
    color_accent_1=[1,0,0,1],
    color_accent_5=[0,0,1,1],
    color_accent_3=[1,1,0,1],
    color_accent_6=[0.5,0,1,1],
    color_highlight=[1,1,1,1],
    color_background=[0,0.5,0,1],
    padding_right=10,
    body_size=12,
    subtitle_size=14,
    logo_size_2=18,
    font_body='DejaVuSans',
)
class FObj:
    theme = fake_theme
kivy.app.App.get_running_app = staticmethod(lambda: FObj())


def run_tests():
    # Use unbound methods to avoid constructing TimelineScreen (which requires App/theme)
    ts = SimpleNamespace()
    # fake graph - create a SimpleGraph with several days
    keys = ["grow_mix","root_mix","bloom_mix","bloom_boost","soil_boost","vit_boost","CalMag"]
    g = SimpleGraph(key=None, color=[1,0,0,1], owner=None, tab_key='food', multi_keys=keys)

    # create a full mapping with several days and volume present
    full = {
        'volume_l': [(0, 1.0), (1, 2.0), (2, 1.0), (3, 2.0)],
        'grow_mix': [(0, 10.0), (1, 20.0), (2, 30.0), (3, 40.0)],
        '_raw': {
            'grow_mix': [(1, 20.0), (3, 40.0)],
            'volume_l': [(1, 2.0), (3, 2.0)]
        }
    }

    # initial apply to set series and get default window
    TimelineScreen._apply_and_preserve_x(ts, g, full)
    # set an arbitrary view window (simulate user scrolled/zoomed)
    g._xmin = 1.0
    g._xmax = 2.5
    g.graph.xmin = g._xmin
    g.graph.xmax = g._xmax

    # now toggle to relative and back, window should be preserved
    rel = TimelineScreen._apply_food_relative(ts, full)
    TimelineScreen._apply_and_preserve_x(ts, g, rel)
    assert abs(g._xmin - 1.0) < 1e-9
    assert abs(g._xmax - 2.5) < 1e-9

    TimelineScreen._apply_and_preserve_x(ts, g, full)
    assert abs(g._xmin - 1.0) < 1e-9
    assert abs(g._xmax - 2.5) < 1e-9

    print('test_food_toggle_preserve passed')

if __name__ == '__main__':
    run_tests()
