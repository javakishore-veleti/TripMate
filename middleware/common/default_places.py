from middleware.common.user_preferences import normalize_places, normalize_preferences

PLACES_SOURCE_USER = "user"
PLACES_SOURCE_SYSTEM = "system_default"

SYSTEM_DEFAULT_PLACES = [
    {"city": "New York", "region": "NY", "postal_code": "", "country": "USA"},
    {"city": "San Francisco", "region": "CA", "postal_code": "", "country": "USA"},
    {"city": "Jaipur", "region": "Rajasthan", "postal_code": "", "country": "India"},
    {"city": "Bangkok", "region": "", "postal_code": "", "country": "Thailand"},
    {"city": "Paris", "region": "", "postal_code": "", "country": "France"},
    {"city": "Barcelona", "region": "", "postal_code": "", "country": "Spain"},
    {"city": "Cairo", "region": "", "postal_code": "", "country": "Egypt"},
    {"city": "Amman", "region": "", "postal_code": "", "country": "Jordan"},
    {"city": "Dubai", "region": "", "postal_code": "", "country": "UAE"},
    {"city": "Abu Dhabi", "region": "", "postal_code": "", "country": "UAE"},
]


def system_default_places() -> list[dict]:
    return [dict(place) for place in SYSTEM_DEFAULT_PLACES]


def resolve_watch_places(preferences: dict | None) -> tuple[list[dict], str]:
    prefs = normalize_preferences(preferences)
    places = normalize_places(prefs.get("places"))
    if places:
        return places, PLACES_SOURCE_USER
    return system_default_places(), PLACES_SOURCE_SYSTEM


def preferences_for_pipeline(preferences: dict | None) -> tuple[dict, str]:
    prefs = normalize_preferences(preferences)
    places, source = resolve_watch_places(prefs)
    prefs["places"] = places
    return prefs, source
