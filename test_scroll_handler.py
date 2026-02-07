"""Unit test to simulate _on_mouse_scroll behavior without Kivy GUI.
This defines a copy of the handler logic but uses a passed-in `window` object
so Kivy imports aren't required. It checks that zoom/scroll are invoked
on the graph-like objects.
"""
from types import SimpleNamespace


def handler(self, window, *args):
    # copied and slightly adapted from timeline_view._on_mouse_scroll
    x = y = scroll_x = scroll_y = 0
    try:
        if len(args) >= 4:
            x, y, scroll_x, scroll_y = args[0], args[1], args[2], args[3]
        elif len(args) == 1:
            ev = args[0]
            scroll_x = getattr(ev, 'scroll_x', 0) or getattr(ev, 'sx', 0) or 0
            scroll_y = getattr(ev, 'scroll_y', 0) or getattr(ev, 'sy', 0) or 0
    except Exception:
        pass

    try:
        raw_mods = getattr(window, 'modifiers', None)
        if raw_mods is None:
            raw_mods = getattr(window, '_modifiers', None)
        mods = [m.lower() for m in (raw_mods or [])]
    except Exception:
        mods = []

    active_text = (self.tabbed_panel.current_tab.text or '').lower()
    key = 'plant' if 'plant' in active_text else ('environment' if 'environment' in active_text else ('water' if 'water' in active_text else ('food' if 'food' in active_text else None)))
    graphs = self.tab_graphs.get(key, [])
    if not graphs:
        return False

    if 'shift' in mods:
        factor = 0.8 if scroll_y > 0 else 1.25
        for g in graphs:
            g.zoom(factor)
    else:
        frac = -0.1 if scroll_y > 0 else 0.1
        for g in graphs:
            g.scroll(frac)

    return True


class DummyGraph:
    def __init__(self):
        self.calls = []

    def zoom(self, factor):
        self.calls.append(('zoom', factor))

    def scroll(self, frac):
        self.calls.append(('scroll', frac))


class DummyWindow:
    def __init__(self, modifiers=None):
        self.modifiers = modifiers


def run_tests():
    # prepare fake self
    fake_tab = SimpleNamespace(current_tab=SimpleNamespace(text='Plant'))
    g1 = DummyGraph()
    g2 = DummyGraph()
    fake_self = SimpleNamespace(tabbed_panel=fake_tab, tab_graphs={'plant':[g1, g2]})

    # simulate scroll up without modifiers (should scroll left -> negative frac)
    win = DummyWindow(modifiers=[])
    ok = handler(fake_self, win, 0, 0, 0, 1)
    assert ok is True
    assert g1.calls and g1.calls[-1][0] == 'scroll'
    print('Scroll without modifiers passed:', g1.calls[-1])

    # reset
    g1.calls.clear()

    # simulate scroll down with shift modifier (should zoom out)
    win2 = DummyWindow(modifiers=['Shift'])
    ok = handler(fake_self, win2, 0, 0, 0, -1)
    assert ok is True
    assert g1.calls and g1.calls[-1][0] in ('zoom',)
    print('Scroll with shift passed:', g1.calls[-1])

    print('All tests passed')


if __name__ == '__main__':
    run_tests()
