"""Tests for services/catalog_service.py - seed catalog lookup."""

from services.catalog_service import get_catalog, lookup_strain, _SEED_CATALOG
import services.catalog_service as _cat_mod


def _setup():
    """Reset the catalog cache."""
    _cat_mod._SEED_CATALOG = None


def test_get_catalog_loads():
    _setup()
    catalog = get_catalog()
    assert isinstance(catalog, list)


def test_get_catalog_not_empty():
    _setup()
    catalog = get_catalog()
    assert len(catalog) > 0, "Catalog should have entries"


def test_get_catalog_entries_are_dicts():
    _setup()
    catalog = get_catalog()
    for entry in catalog[:5]:  # check first 5
        assert isinstance(entry, dict), f"Expected dict, got {type(entry)}"


def test_get_catalog_cached():
    _setup()
    c1 = get_catalog()
    c2 = get_catalog()
    assert c1 is c2, "Second call should return cached object"


def test_lookup_strain_not_found():
    _setup()
    result = lookup_strain("zzz_nonexistent_strain_zzz")
    assert result is None


def test_lookup_strain_empty_string():
    _setup()
    result = lookup_strain("")
    assert result is None


def test_lookup_strain_none():
    _setup()
    result = lookup_strain(None)
    assert result is None


def test_lookup_strain_found():
    """Use the first entry in the catalog to verify lookup works."""
    _setup()
    catalog = get_catalog()
    if not catalog:
        return  # skip if catalog is empty (shouldn't happen)
    first = catalog[0]
    strain_name = first.get("strain", "")
    if not strain_name:
        return
    result = lookup_strain(strain_name)
    assert result is not None, f"Expected to find strain '{strain_name}'"
    assert result["strain"] == strain_name


def test_lookup_strain_case_insensitive():
    """Lookup should work regardless of case."""
    _setup()
    catalog = get_catalog()
    if not catalog:
        return
    first = catalog[0]
    strain_name = first.get("strain", "")
    if not strain_name:
        return
    result = lookup_strain(strain_name.upper())
    assert result is not None, f"Case-insensitive lookup failed for '{strain_name.upper()}'"
