"""services - Business logic layer (no Kivy imports).

Re-exports for convenience.  All functions depend only on the data layer
(``data.py``), ``constants.py``, ``helpers.py``, ``validators.py``, and stdlib.
"""

from services.garden_service import (
    get_garden_plants_view,
    filter_plants,
    sort_plants,
)
from services.plant_service import (
    create_plant,
    apply_event_side_effects,
)
from services.event_service import (
    get_events_sorted,
    add_event,
)
from services.settings_service import (
    get_shader_prefs,
    has_password,
    get_theme_name,
    get_settings,
    set_setting,
)
from services.catalog_service import (
    lookup_strain,
    get_catalog,
)
from services.formatting import (
    format_relative_time,
    get_health_indicator,
    get_nutrient_status,
)
