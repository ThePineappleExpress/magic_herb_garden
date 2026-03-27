"""catalog_service.py - Seed catalog lookup.

Extracted from sow_seed.py.  No Kivy imports.
"""

import json
import logging
import os
from pathlib import Path

LOG = logging.getLogger(__name__)

_PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(__file__)))
_CATALOG_FILE = _PROJECT_ROOT / "bin" / "db" / "seed_catalog.json"

_SEED_CATALOG: list | None = None


def _load_catalog() -> list:
    """Read the seed catalog from disk."""
    try:
        with open(_CATALOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        LOG.exception("Failed to load seed catalog from %s", _CATALOG_FILE)
        return []


def get_catalog() -> list:
    """Return the cached seed catalog (list of dicts)."""
    global _SEED_CATALOG
    if _SEED_CATALOG is None:
        _SEED_CATALOG = _load_catalog()
    return _SEED_CATALOG


def lookup_strain(strain_name: str) -> dict | None:
    """Case-insensitive lookup of a strain in the seed catalog.

    Returns the catalog record dict, or None if not found.
    """
    if not strain_name:
        return None
    lower = strain_name.strip().lower()
    catalog = get_catalog()
    return next(
        (r for r in catalog if r.get("strain", "").strip().lower() == lower),
        None,
    )
