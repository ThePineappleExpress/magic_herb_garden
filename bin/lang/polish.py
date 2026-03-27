APP_TITLE = "Magic Herb Tracker"

# Common buttons
BUTTON_SAVE = "Zapisz"
BUTTON_CONFIRM = "Potwierdź"
BUTTON_CANCEL = "Anuluj"
BUTTON_ADD = "Dodaj"
BUTTON_DELETE = "Usuń"
BUTTON_PLUS = "+"
BUTTON_MINUS = "-"
BUTTON_EDIT = "edytuj"

# Generic labels
LABEL_NAME = "Nazwa"
LABEL_TYPE = "Typ"
LABEL_QUANTITY = "Ilość"

# Messages
MSG_CONFIRM_DELETE = "Czy na pewno chcesz usunąć ten element?"
MSG_CONFIRM_DELETE_PLANT = "Czy na pewno chcesz usunąć wybraną roślinę?"
MSG_CONFIRM_CANCEL_CHANGES = "Czy na pewno chcesz anulować i utracić wszystkie niezapisane zmiany?"

# Confirmation prompt title and variants
ARE_YOU_SURE_TITLE = "Czy jesteś pewien?"
MSG_CONFIRM_CANCEL = "Odrzucić zmiany?"
MSG_CONFIRM_EXIT = "Opuścić ogród?"

# Relative / time labels
TODAY = "Dzisiaj"
YESTERDAY = "Wczoraj"
DAYS_AGO = "{n} dni temu"
WEEK_AGO_ONE = "{n} tydzień temu"
WEEK_AGO_PLURAL = "{n} tygodni temu"
MONTH_AGO_ONE = "{n} miesiąc temu"
MONTH_AGO_PLURAL = "{n} miesięcy temu"
YEAR_AGO_ONE = "{n} rok temu"
YEAR_AGO_PLURAL = "{n} lat temu"

# Generic labels
BACK = "Wstecz"
DAY_LABEL = "Dzień"

# Plant details / health
HEALTH_HEALTHY = "Zdrowa"
HEALTH_MINOR = "Drobne problemy"
HEALTH_MODERATE = "Umiarkowane problemy"
HEALTH_SEVERE = "Poważne problemy"
STATUS_FLOWERING = "Kwitnie!"
STATUS_HARVESTED = "Zebrano!"

# Event toggle labels
TOGGLE_TOP = "Szczytowanie"
TOGGLE_PRUNE = "Przycinanie"
TOGGLE_FLIP = "Przełącz"
FLIP_DONE = "Przełączono"

# Event / plant field titles
EVENT_FIELD_TITLES = {
  "HEIGHT": "Wysokość",
  "NODES": "Węzły",
  "SPACING": "Rozstaw",
  "MAIN_STEMS": "Główne łodygi",
  "COLOR": "Kolor",
  "MORPHOLOGY": "Morfologia",
  "AIR_TEMP": "Temp. powietrza",
  "HUMIDITY": "Wilgotność",
  "VPD": "VPD",
  "SOIL_PH": "pH gleby",
  "SOIL": "Gleba",
  "PPFD": "PPFD",
  "LIGHT": "Światło",
}

WATER_FIELD_TITLES = {
  "VOLUME": "Objętość",
  "TEMP": "Temp.",
  "PH": "pH",
  "PPM": "PPM",
}

# Common small labels
NAME_SEPARATOR = " | "

# Last event templates
LAST_WATER_TEMPLATE = "Ostatnie podlewanie: {vol} L, pH {ph}, {ppm} ppm @ {ts}"
LAST_EVENT_TEMPLATE = "Ostatnie zdarzenie: {type} @ {ts}"

# Screen titles (used in various views)
SCREEN_TITLE_GARDEN = "Mój magiczny [color={color}]OGRÓD[/color]"
SCREEN_TITLE_DETAILS = "Tylko spójrz na tę [color={color}]PIĘKNOŚĆ[/color]"
SCREEN_TITLE_GRAPH = "Tylko spójrz na tę [color={color}]PIĘKNOŚĆ[/color]"
SCREEN_TITLE_ENV = "Gdzie będę to [color={color}]UPRAWIAĆ[/color]?"
SCREEN_TITLE_SOW_SEED = "Powiedz coś o swoim [color={color}]nasionie[/color]"
SCREEN_TITLE_ADD_GARDEN = "Stwórz nowy [color={color}]OGRÓD[/color]"
SCREEN_TITLE_SELECT_GARDEN = "Wybierz [color={color}]OGRÓD[/color]"
SCREEN_SETTINGS_TITLE = "Dostosujmy [color={color}]USTAWIENIA[/color]"
SCREEN_TITLE_PASSWORD = "Wprowadź swoje [color={color}]HASŁO[/color]"


# Timeline tab labels
TAB_PLANT = "Roślina"
TAB_ENVIRONMENT = "Środowisko"
TAB_WATER = "Woda"
TAB_FOOD = "Odżywianie"

# Set environment
SET_ENV_WARNING_TITLE = "Podlewanie i nawożenie:"
SET_ENV_WARNING_BODY = (
    "Sprawdź opakowanie lub hodowcę w celu uzyskania szacunkowych profili.\n"
    "Wartości dostosują się automatycznie w trakcie życia rośliny.\n"
    "Jeśli nie jesteś pewien, zostaw oba suwaki w domyślnej pozycji."
)

# Sow seed / fields
SEEDBANK_LABEL = "Bank nasion: "
HINT_SELECT_NAME = "Wybierz nazwę dla swojej rośliny"
STRAIN_LABEL = "Odmiana: "
HINT_WHATS_ON_BOX = "Co jest na opakowaniu?"
INFO_LABEL = "Info: "
HINT_SAY_SOMETHING = "Powiedz coś o swojej roślinie"
HERITAGE_LABEL = "Dziedzictwo: "
GENES_SATIVA = "Sativa"
GENES_INDICA = "Indica"
GENES_HYBRID = "Hybryda"
TYPE_LABEL = "Typ: "
TYPE_AUTOMATIC = "Automatyczna"
TYPE_PHOTOPERIODIC = "Fotoperiodyczna"
FLOWERING_PERIOD_LABEL = "Okres kwitnienia: "
HINT_DAYS_TO_FLOWER = "Dni do kwitnienia"

# Buttons
NEXT = "Dalej"

# Feeding / dropdown field labels (used in feeding rows)
FEED_VEG = "Wzrost"
FEED_ROOT = "Korzeń"
FEED_SOIL = "Gleba"
FEED_VIT = "Wit"

FEED_FLOWER = "Kwiat"
FEED_TOPS = "Wierzchołki"
FEED_CALMAG = "CalMag"
FEED_FUNGI = "Grzyby"

# Notes label
LABEL_NOTES = "Notatki"
NUTRIENTS = "Składniki"
VIEW_TIMELINE = "Zobacz\nOś czasu"

# Generic confirmations
YES = "Tak"
NO = "Nie"

# Fertilizer / medium strings
FERTILIZED_LABEL = "Nawożone: "
FERTILIZED = "Nawożone"
BARE = "Bez nawozu"
YOUR_FERTILIZER_LABEL = "Twój nawóz: "
FERTILIZER_ORGANIC = "Organiczny"
FERTILIZER_MINERAL = "Mineralny"

# Environment defaults
EVERY_3_DAYS = "Co 3 dni"
EVERY_2ND_WATERING = "Co 2. podlewanie"
POT_LABEL_DEFAULT = "9L"

# Set environment labels
WATERING_LABEL = "Podlewanie"
FEEDING_LABEL = "Nawożenie"
POT_SIZE_LABEL = "Wielkość doniczki"
MEDIUM_LABEL = "Podłoże"
MEDIUM_SOIL = "Ziemia"
MEDIUM_COCO = "Kokos"
MEDIUM_MINERAL = "Mineralne"
MEDIUM_HYDRO = "Hydro"

# Additional frequency templates
EVERY_WATERING = "Przy każdym podlewaniu"
EVERY_3RD_WATERING = "Co 3. podlewanie"
EVERY_N_DAYS = "Co {n} dni"

# Pot size format
POT_SIZE_FMT = "{n}L"

# Numeric/hint defaults
HINT_NUM_DEFAULT = "0.0"
HINT_AIR_TEMP_DEFAULT = "24"
HINT_RH_DEFAULT = "55"

# Misc small tokens
DASH = "–"

# Graph/button small labels
GRAPH_BTN_ABSOLUTE = "Bezwzględne"
ML_PER_LITER = "ml na litr"
ML = "ml"

# Settings screen
SETTINGS_CURRENT_PASSWORD = "Aktualne hasło: "
SETTINGS_PASSWORD = "Nowe hasło: "
HINT_CURRENT_PASSWORD = "Wprowadź aktualne hasło"
HINT_NO_PASSWORD_SET = "Nie ustawiono hasła"
SETTINGS_PASSWORD_CONFIRM = "Potwierdź hasło: "
SETTINGS_DB_PATH = "Ścieżka bazy danych: "
SETTINGS_SHADER_TOGGLE = "Animowane tło: "
HINT_ENTER_PASSWORD = "Wprowadź hasło"
HINT_CONFIRM_PASSWORD = "Potwierdź hasło"
HINT_DB_PATH = "Ścieżka do folderu bazy danych"
SETTINGS_SHADER_ON = "Wł."
SETTINGS_SHADER_OFF = "Wył."
SETTINGS_THEME = "Motyw: "
SETTINGS_SHADER_SELECT = "Styl shadera: "
SETTINGS_SHADER_RELOAD = "Odśwież"
SETTINGS_PIXEL_SCALE = "Skala pikseli: "
SETTINGS_REMOVE_PASSWORD = "Usuń hasło"
WARN_SET_PASSWORD = "UWAGA: Ustawienie hasła zaszyfruje całą bazę danych.\nJeśli zapomnisz lub zgubisz hasło, nie będziesz mógł odzyskać swoich danych.\nCzy na pewno chcesz kontynuować?"
WARN_REMOVE_PASSWORD = "Czy na pewno chcesz usunąć ochronę hasłem i odszyfrować bazę danych?\nTwoje dane będą przechowywane w postaci zwykłego JSON po tej operacji."
WARN_MOVE_DB_PATH = "Spowoduje to przeniesienie wszystkich plików ogrodów i roślin do nowej lokalizacji.\nAplikacja uruchomi się ponownie automatycznie po przeniesieniu.\nCzy na pewno chcesz kontynuować?"
SETTINGS_SELECT_FOLDER = "Wybierz"
SETTINGS_LANGUAGE = "Język: "
SETTINGS_LANGUAGE_RESTART = "(wymagany restart)"

# Sort / filter bar
SORT_BY = "Sortuj wg:"
SORT_NAME = "Nazwa"
SORT_BREEDER = "Hodowca"
SORT_DATE_PLANTED = "Data posadzenia"
SORT_DATE_CREATED = "Data utworzenia"
SORT_DAYS_TO_HARVEST = "Dni do zbiorów"
SORT_DAYS_TO_WATER = "Dni do podlania"
SORT_MEDIUM = "Podłoże"
SORT_PLANT_COUNT = "Rośliny"
SORT_NEXT_EVENT = "Następne zdarzenie"
SORT_LAST_PLANTED = "Ostatnio posadzone"
SORT_LAST_EVENT = "Ostatnie zdarzenie"
SORT_TYPE = "Typ"
SORT_ASCENDING = "Rosnąco"
SORT_DESCENDING = "Malejąco"
FILTER_ACTIVE_ONLY = "Tylko aktywne"
SEARCH_HINT = "Szukaj..."

# Garden list legend headers
LEGEND_GENES = "Geny"
LEGEND_PLANT = "Roślina"
LEGEND_MEDIUM = "Podłoże"
LEGEND_LAST_WATER = "Ost. podlewanie"
LEGEND_NEXT_WATER = "Nast. podlewanie"
LEGEND_FLOWER = "Kwitnienie"
LEGEND_HARVEST = "Zbiory"
LEGEND_GARDEN_NAME = "Ogród"
LEGEND_GARDEN_TYPE = "Typ"
LEGEND_PLANT_COUNT = "Rośliny"

# Garden / header buttons
OPTIONS = "Opcje"
EXIT_APP = "Zamknij\nAplikację"
EXIT_GARDEN = "Opuść\nOgród"
ENTER_GARDEN = "Wejdź do ogrodu"
ADD_PLANT = "Dodaj roślinę"
ADD_GARDEN = "Dodaj ogród"
SELECT_GARDEN = "Wybierz ogród"
VIEW_GARDENS = "Zobacz\nOgrody"
DELETE_GARDEN = "Usuń ogród"
MSG_CONFIRM_DELETE_GARDEN = "Czy na pewno chcesz usunąć wybrany ogród i wszystkie rośliny w nim?"
VIEW_SELECTED_PLANT = "Zobacz wybraną roślinę"
DELETE_SELECTED_PLANT = "Usuń wybraną roślinę"

# Password check screen
PW_TOO_MANY_ATTEMPTS = "Zbyt wiele prób. Poczekaj {n}s."
PW_WRONG_PASSWORD = "Złe hasło. Poczekaj {n}s przed ponowną próbą."
PW_BUTTON_UNLOCK = "Odblokuj"

# Add event
HINT_EVENT_NOTES = "Powiedz, co wydarzyło się dzisiaj..."

# Garden management screens
GARDEN_NAME_LABEL = "Nazwa ogrodu: "
HINT_GARDEN_NAME = "Nazwij swój ogród"
GARDEN_TYPE_LABEL = "Typ: "
GARDEN_TYPE_INDOOR = "Wewnętrzny"
GARDEN_TYPE_OUTDOOR = "Zewnętrzny"
LIGHT_TYPE_LABEL = "Typ oświetlenia: "
LIGHT_WATTAGE_LABEL = "Moc: "
HINT_LIGHT_WATTAGE = "Waty"
LIGHT_SCHEDULE_LABEL = "Harmonogram oświetlenia: "
HINT_LIGHT_HOURS = "Godziny świecenia"
LOCATION_LABEL = "Lokalizacja: "

# Light types
LIGHT_LED = "LED"
LIGHT_HPS = "HPS"
LIGHT_CFL = "CFL"

# Climate regions
CLIMATE_NH_TEMPERATE = "Pn. półkula umiarkowana"
CLIMATE_MEDITERRANEAN = "Śródziemnomorski"
CLIMATE_TROPICAL = "Tropikalny"
CLIMATE_SH_TEMPERATE = "Pd. półkula umiarkowana"
CLIMATE_EQUATORIAL = "Równikowy"

# Location cascading dropdowns (outdoor gardens)
CONTINENT_LABEL = "Kontynent: "
COUNTRY_LABEL = "Kraj: "
CITY_LABEL = "Miasto: "


LEGEND_TITLES = {
  "plant_height": "Wysokość rośliny (cm)",
  "num_nodes": "Liczba węzłów",
  "node_spacing": "Rozstaw węzłów (cm)",
  "main_stem_number": "Liczba głównych łodyg",
  "air_temp_c": "Temperatura powietrza (°C)",
  "rh_percent": "Wilgotność względna (%)",
  "soil_moisture": "Wilgotność gleby",
  "soil_ph": "pH gleby",
  "vpd_kpa": "VPD (kPa)",
  "ppfd": "PPFD (µmol/m²/s)",
  "volume_l": "Objętość wody (L)",
  "water_temp_c": "Temperatura wody (°C)",
  "ph": "pH wody",
  "ppm": "PPM wody",
}

# Export / Import screen
EXPORT_IMPORT_TITLE = "Udostępnij i zabezpiecz swój [color={color}]SKARB[/color]"
EXPORT_SELECT_GARDENS = "Wybierz ogrody:"
EXPORT_SELECT_ALL = "Zaznacz wszystko"
EXPORT_DESELECT_ALL = "Odznacz wszystko"
EXPORT_TYPE_LABEL = "Typ eksportu:"
EXPORT_SAFE = "Bezpieczny (szyfrowany)"
EXPORT_OPEN = "Otwarty (bez hasła)"
EXPORT_PASSWORD = "Hasło eksportu:"
EXPORT_PASSWORD_CONFIRM = "Potwierdź hasło:"
EXPORT_FILENAME_LABEL = "Nazwa pliku:"
EXPORT_CHOOSE_LOCATION = "Wybierz lokalizację eksportu"
BUTTON_EXPORT = "Eksportuj"
BUTTON_IMPORT = "Importuj"
EXPORT_NO_GARDENS_SELECTED = "Wybierz co najmniej jeden ogród do eksportu."
EXPORT_SUCCESS = "Eksport zakończony:"
EXPORT_ERROR = "Eksport nie powiódł się:"
IMPORT_CHOOSE_FILE = "Wybierz plik .weed do importu"
IMPORT_PASSWORD_PROMPT = "Ten plik jest zaszyfrowany. Wprowadź hasło eksportu:"
IMPORT_CONFLICT_WARNING = "{n} ogród(ów) w tym pliku już istnieje i zostanie nadpisany(ch).\nCzy na pewno chcesz kontynuować?"
IMPORT_ERROR_CORRUPT = "Plik wydaje się uszkodzony lub nie jest prawidłowym plikiem .weed."
IMPORT_ERROR_WRONG_PW = "Złe hasło lub plik jest uszkodzony."
IMPORT_SUCCESS = "Import zakończony: zaimportowano {gardens} ogród(ów) i {events} plik(ów) zdarzeń."
SETTINGS_EXPORT_IMPORT = "Eksport / Import danych"
SETTINGS_EXPORT_CSV = "Eksportuj do CSV"
CSV_EXPORT_TITLE = "Eksportuj ogrody do [color={color}]CSV[/color]"
CSV_EXPORT_CHOOSE_LOCATION = "Wybierz lokalizację eksportu"
CSV_EXPORT_FILENAME_LABEL = "Nazwa pliku:"
CSV_EXPORT_SUCCESS = "Eksport CSV zakończony:"
CSV_EXPORT_ERROR = "Eksport CSV nie powiódł się:"
CSV_EXPORT_NO_GARDENS = "Wybierz co najmniej jeden ogród do eksportu."

# Photos
PHOTOS_TITLE = "Zdjęcia"
PHOTO_ADD = "Dodaj zdjęcie"
PHOTO_VIEW = "Zobacz zdjęcie"
PHOTO_DELETE = "Usuń zdjęcie"
PHOTO_VIEW_GALLERY = "Zobacz\nGalerię"
PHOTO_SHOW_GALLERY = "Pokaż\nGalerię"
PHOTO_NONE = "Brak zdjęć"
MSG_CONFIRM_DELETE_PHOTO = "Czy na pewno chcesz usunąć to zdjęcie?"
PHOTO_GALLERY_TITLE = "Twoja [color={color}]GALERIA[/color]"

import sys

def get(key: str) -> str:
    """Return the string for a constant-like key, or the key itself."""
    return getattr(sys.modules[__name__], key, key)
