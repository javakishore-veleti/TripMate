MAX_INTEREST_PLACES = 5
DEFAULT_EVENT_RADIUS_MILES = 200

DEFAULT_PREFERENCES = {
    "home_city": "",
    "home_country": "",
    "typical_budget": "",
    "currency": "USD",
    "travel_style": "",
    "pace": "",
    "interests": [],
    "companions": "",
    "avoid": "",
    "notes": "",
    "places": [],
    "event_radius_miles": DEFAULT_EVENT_RADIUS_MILES,
    "llm_provider": "ollama",
    "llm_model": "",
    "llm_base_url": "",
    "llm_jobs": {},
}

LLM_JOB_KEYS = ("classify", "reason", "deep")

_PROFILE_LABELS = {
    "home_city": "Home city",
    "home_country": "Home country",
    "typical_budget": "Typical budget",
    "currency": "Currency",
    "travel_style": "Travel style",
    "pace": "Pace",
    "interests": "Interests",
    "companions": "Traveling with",
    "avoid": "Avoid",
    "notes": "Notes",
}


def empty_place() -> dict:
    return {"city": "", "region": "", "postal_code": "", "country": ""}


def empty_preferences() -> dict:
    data = {}
    for key, value in DEFAULT_PREFERENCES.items():
        if isinstance(value, list):
            data[key] = []
        elif isinstance(value, dict):
            data[key] = {}
        else:
            data[key] = value
    return data


def normalize_place(raw: dict | None) -> dict | None:
    if not isinstance(raw, dict):
        return None
    place = {
        "city": str(raw.get("city") or "").strip(),
        "region": str(raw.get("region") or raw.get("state") or "").strip(),
        "postal_code": "",
        "country": str(raw.get("country") or "").strip(),
    }
    if not place["city"]:
        return None
    return place


def empty_llm_job(provider: str = "ollama", model: str = "") -> dict:
    return {"provider": provider or "ollama", "model": model or ""}


def normalize_llm_jobs(raw, fallback_provider: str = "ollama", fallback_model: str = "") -> dict:
    source = raw if isinstance(raw, dict) else {}
    jobs = {}
    for key in LLM_JOB_KEYS:
        item = source.get(key)
        if not isinstance(item, dict):
            item = {}
        jobs[key] = empty_llm_job(
            str(item.get("provider") or fallback_provider or "ollama").strip(),
            str(item.get("model") or fallback_model or "").strip(),
        )
    return jobs


def normalize_places(raw) -> list[dict]:
    if not isinstance(raw, list):
        return []
    places: list[dict] = []
    for item in raw:
        place = normalize_place(item)
        if place:
            places.append(place)
        if len(places) >= MAX_INTEREST_PLACES:
            break
    return places


def normalize_radius(value) -> int:
    try:
        miles = int(value)
    except (TypeError, ValueError):
        miles = DEFAULT_EVENT_RADIUS_MILES
    return max(25, min(2000, miles))


def format_place(place: dict | None) -> str:
    if not place:
        return ""
    bits = [
        str(place.get("city") or "").strip(),
        str(place.get("region") or "").strip(),
        str(place.get("country") or "").strip(),
    ]
    return ", ".join(bit for bit in bits if bit)


def normalize_preferences(raw: dict | None) -> dict:
    normalized = empty_preferences()
    if not isinstance(raw, dict):
        return normalized
    for key, default in DEFAULT_PREFERENCES.items():
        if key in {"places", "event_radius_miles", "llm_jobs"} or key not in raw:
            continue
        value = raw[key]
        if isinstance(default, list):
            if isinstance(value, str):
                normalized[key] = [part.strip() for part in value.split(",") if part.strip()]
            elif isinstance(value, list):
                normalized[key] = [str(item).strip() for item in value if str(item).strip()]
        else:
            normalized[key] = str(value or "").strip()
    if not normalized["currency"]:
        normalized["currency"] = "USD"
    if "places" in raw:
        normalized["places"] = normalize_places(raw.get("places"))
    if "event_radius_miles" in raw:
        normalized["event_radius_miles"] = normalize_radius(raw.get("event_radius_miles"))
    else:
        normalized["event_radius_miles"] = DEFAULT_EVENT_RADIUS_MILES
    normalized["llm_jobs"] = normalize_llm_jobs(
        raw.get("llm_jobs") if isinstance(raw, dict) else {},
        normalized.get("llm_provider") or "ollama",
        normalized.get("llm_model") or "",
    )
    return normalized


def preferences_are_empty(prefs: dict | None) -> bool:
    data = normalize_preferences(prefs)
    for key, value in data.items():
        if key == "currency" and value == "USD":
            continue
        if key == "event_radius_miles" and value == DEFAULT_EVENT_RADIUS_MILES:
            continue
        if key == "llm_provider" and value == "ollama":
            continue
        if key in {"llm_model", "llm_base_url", "llm_jobs"}:
            continue
        if isinstance(value, list):
            if value:
                return False
        elif str(value).strip():
            return False
    return True


def traveler_profile_block(prefs: dict | None) -> str:
    data = normalize_preferences(prefs)
    if preferences_are_empty(data):
        return ""
    lines = [
        "Traveler profile (honor these defaults unless the current request clearly overrides them):"
    ]
    for key, label in _PROFILE_LABELS.items():
        value = data.get(key)
        if not value or (key == "currency" and value == "USD" and not data.get("typical_budget")):
            continue
        if isinstance(value, list):
            value = ", ".join(value)
        lines.append(f"- {label}: {value}")
    if data["places"]:
        lines.append(
            "- Places they live or watch: "
            + "; ".join(format_place(place) for place in data["places"])
        )
        lines.append(f"- Event search radius: {data['event_radius_miles']} miles")
    return "\n".join(lines)


def apply_preferences_to_constraints(constraints: dict, prefs: dict | None) -> dict:
    data = normalize_preferences(prefs)
    if not str(constraints.get("origin") or "").strip():
        if data["home_city"]:
            origin = data["home_city"]
            if data["home_country"]:
                origin = f"{origin}, {data['home_country']}"
            constraints["origin"] = origin
        elif data["places"]:
            constraints["origin"] = format_place(data["places"][0])
    if not str(constraints.get("budget") or "").strip() and data["typical_budget"]:
        budget = data["typical_budget"]
        if data["currency"]:
            budget = f"{budget} {data['currency']}"
        constraints["budget"] = budget
    if not str(constraints.get("travel_style") or "").strip() and data["travel_style"]:
        constraints["travel_style"] = data["travel_style"]
    extras = list(constraints.get("special_preferences") or [])
    for item in data["interests"] + [data["avoid"]]:
        text = str(item or "").strip()
        if text and text not in extras:
            extras.append(text)
    constraints["special_preferences"] = extras
    return constraints
