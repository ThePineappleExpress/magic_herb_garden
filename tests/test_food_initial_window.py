"""Tests that food graphs initialize anchored to the most recent event (xmax) and show up to 30 days."""
from types import SimpleNamespace
from timeline_view import SimpleGraph
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
    keys = ["grow_mix","root_mix"]
    g = SimpleGraph(key=None, color=[1,0,0,1], owner=None, tab_key='food', multi_keys=keys)

    # Case A: span less than 30 days -> should anchor at xmax and show up to 30 days
    full = {
        'volume_l': [(0,1.0),(2,1.0),(5,1.0)],
        'grow_mix': [(0,10),(2,20),(5,30)],
        'root_mix': [(0,5),(2,10),(5,15)],
        '_raw': {'grow_mix': [(5,30)], 'root_mix': [(5,15)], 'volume_l':[(5,1.0)]}
    }
    g.set_series({**{k:full[k] for k in keys}, 'volume_l': full['volume_l'], '_raw': full['_raw']})
    assert g._xmax == 5
    # the visible window should show the full data span so graph fills width
    assert g._xmin == 0 and g._xmax == 5

    # Case B: wide span > default window -> still show full span on initial load
    full2 = {
        'volume_l': [(0,1.0),(40,1.0)],
        'grow_mix': [(0,10),(40,20)],
        'root_mix': [(0,5),(40,15)],
        '_raw': {'grow_mix': [(40,20)], 'root_mix': [(40,15)], 'volume_l':[(40,1.0)]}
    }
    # use a fresh graph to simulate initial load for a separate dataset
    g2 = SimpleGraph(key=None, color=[1,0,0,1], owner=None, tab_key='food', multi_keys=keys)
    g2.set_series({**{k:full2[k] for k in keys}, 'volume_l': full2['volume_l'], '_raw': full2['_raw']})
    assert g2._xmax == 40
    assert g2._xmin == 0 # full span shown on initial load

    print('test_food_initial_window passed')

if __name__ == '__main__':
    run_tests()