import storage


def test_normalize_plants_none():
    assert storage._normalize_plants(None) == []


def test_normalize_plants_list_non_dict_items_skipped():
    data = [{"id": "1"}, "x", 42, None]
    out = storage._normalize_plants(data)
    assert out == [{"id": "1"}]


def test_normalize_plants_flat_list():
    data = [{"id": "1"}, {"id": "2"}]
    out = storage._normalize_plants(data)
    assert [p["id"] for p in out] == ["1", "2"]


def test_normalize_plants_invalid():
    assert storage._normalize_plants(123) == []
