"""Ensure _apply_and_preserve_x uses full span when graph uninitialized."""
import kivy.app
from types import SimpleNamespace
from timeline_view import TimelineScreen, SimpleGraph

# fake theme
fake_theme = SimpleNamespace(color_transparent=[0,0,0,0.5],color_accent_highlight_2=[0,1,0,1],color_accent_7=[0.5,0.2,0,1],color_accent_2=[1,0.5,0,1],color_accent_1=[1,0,0,1],color_accent_5=[0,0,1,1],color_accent_3=[1,1,0,1],color_accent_6=[0.5,0,1,1],color_highlight=[1,1,1,1],color_background=[0,0.5,0,1],padding_right=10,body_size=12,subtitle_size=14,logo_size_2=18,font_body='DejaVuSans',color_accent_highlight_1=[1,0.9,0.5,1])
class FObj:
    theme = fake_theme
    def go_back(self,*a,**k):
        pass
kivy.app.App.get_running_app = staticmethod(lambda: FObj())


def run_tests():
    ts = TimelineScreen()
    keys = ["grow_mix","root_mix"]
    g = SimpleGraph(key=None, color=[1,0,0,1], owner=ts, tab_key='food', multi_keys=keys)

    # simulate uninitialized graph (defaults in place)
    assert g._xmin == 0 and g._xmax == 10
    mapping = {
        'grow_mix': [(0,10),(5,20)],
        'root_mix': [(0,5),(5,15)],
        'volume_l': [(0,1),(5,1)],
        '_raw': {'grow_mix': [(5,20)], 'root_mix': [(5,15)], 'volume_l':[(5,1)]}
    }
    # apply via helper which should detect uninitialized and call set_series -> full span
    ts._apply_and_preserve_x(g, mapping)
    assert g._xmin == 0 and g._xmax == 5
    print('test_apply_and_preserve_initial passed')

if __name__ == '__main__':
    run_tests()
