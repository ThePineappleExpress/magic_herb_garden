"""Simple test for the food relative-per-liter transformation.
Run as a script: python tests/test_food_relative.py
"""
from timeline_view import TimelineScreen


def run_tests():
    full = {
        'volume_l': [(0, 0.5), (1, 1.0), (2, 0.0)],
        'grow_mix': [(0, 10.0), (1, 20.0), (2, 15.0)],
        '_raw': {
            'volume_l': [(0, 0.5), (1, 1.0)],
            'grow_mix': [(1, 20.0)]
        }
    }

    res = TimelineScreen._apply_food_relative(None, full)

    # filled series: divided by filled volume_l
    assert abs(res['grow_mix'][0][1] - (10.0 / 0.5)) < 1e-9
    assert abs(res['grow_mix'][1][1] - (20.0 / 1.0)) < 1e-9
    # third day volume is zero -> result should fall back to absolute (15.0)
    assert abs(res['grow_mix'][2][1] - 15.0) < 1e-9

    # raw series: should use raw volume_l first (day 1 has both present)
    assert abs(res['_raw']['grow_mix'][0][1] - (20.0 / 1.0)) < 1e-9

    print('test_apply_food_relative passed')


if __name__ == '__main__':
    run_tests()
