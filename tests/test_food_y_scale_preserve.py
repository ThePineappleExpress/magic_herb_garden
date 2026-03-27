"""Test the y-scale preservation when toggling food relative/absolute."""
from types import SimpleNamespace
from timeline_view import SimpleGraph, TimelineScreen
import kivy.app

# provide fake theme
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
    keys = ["grow_mix","root_mix","bloom_mix","bloom_boost","soil_boost","vit_boost","CalMag"]
    g = SimpleGraph(key=None, color=[1,0,0,1], owner=None, tab_key='food', multi_keys=keys)

    full = {
        'volume_l': [(0, 1.0), (1, 2.0), (2, 1.0)],
        'grow_mix': [(0, 10.0), (1, 20.0), (2, 30.0)],
        '_raw': {
            'grow_mix': [(1, 20.0)],
            'volume_l': [(1, 2.0)]
        }
    }
    ts = SimpleNamespace()
    # Apply absolute and record y range
    TimelineScreen._apply_and_preserve_x(ts, g, full)
    ymin = float(g.graph.ymin)
    ymax = float(g.graph.ymax)

    # Now apply relative; because absolute y-range exists it should stay the same
    rel = TimelineScreen._apply_food_relative(ts, full)
    TimelineScreen._apply_and_preserve_x(ts, g, rel)
    # apply stored absolute y-range
    if hasattr(ts, '_last_food_ymin') and ts._last_food_ymin is not None:
        g.graph.ymin = ts._last_food_ymin
    if hasattr(ts, '_last_food_ymax') and ts._last_food_ymax is not None:
        g.graph.ymax = ts._last_food_ymax

    assert abs(float(g.graph.ymin) - ymin) < 1e-9
    assert abs(float(g.graph.ymax) - ymax) < 1e-9

    print('test_food_y_scale_preserve passed')

if __name__ == '__main__':
    run_tests()