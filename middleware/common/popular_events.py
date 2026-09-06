from csv import DictReader
from datetime import date
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent / "data"
_CITIES_FILE = _DATA_DIR / "popular_cities.csv"
_EVENTS_FILE = _DATA_DIR / "popular_city_events.csv"
_KINDS = {"festival", "culture", "season", "community"}


def _split_keys(raw: str) -> list[str]:
    return [part.strip().lower() for part in str(raw or "").replace(",", "|").split("|") if part.strip()]


def _split_months(raw: str) -> list[int]:
    months: list[int] = []
    for part in str(raw or "").replace("|", ",").split(","):
        part = part.strip()
        if part.isdigit():
            value = int(part)
            if 1 <= value <= 12:
                months.append(value)
    return months


@lru_cache(maxsize=1)
def load_popular_cities() -> list[dict]:
    rows: list[dict] = []
    with _CITIES_FILE.open(newline="", encoding="utf-8") as handle:
        for row in DictReader(handle):
            city = str(row.get("city") or "").strip()
            if not city:
                continue
            aliases = _split_keys(row.get("aliases") or "")
            aliases.append(city.lower())
            rows.append(
                {
                    "city": city,
                    "region": str(row.get("region") or "").strip(),
                    "country": str(row.get("country") or "").strip(),
                    "aliases": list(dict.fromkeys(aliases)),
                }
            )
    return rows


@lru_cache(maxsize=1)
def load_popular_events() -> list[dict]:
    rows: list[dict] = []
    with _EVENTS_FILE.open(newline="", encoding="utf-8") as handle:
        for row in DictReader(handle):
            name = str(row.get("name") or "").strip()
            months = _split_months(row.get("months") or "")
            if not name or not months:
                continue
            kind = str(row.get("kind") or "culture").strip().lower()
            if kind == "food":
                kind = "festival"
            if kind not in _KINDS:
                kind = "culture"
            keys = _split_keys(row.get("match_keys") or "")
            city = str(row.get("city") or "").strip()
            if city:
                keys.append(city.lower())
            rows.append(
                {
                    "months": months,
                    "keys": list(dict.fromkeys(keys)),
                    "name": name,
                    "kind": kind,
                    "city": city,
                    "region": str(row.get("region") or "").strip(),
                    "country": str(row.get("country") or "").strip(),
                    "when": str(row.get("when") or "").strip(),
                    "blurb": str(row.get("blurb") or "").strip(),
                }
            )
    return rows


def _haystack(places: list[str]) -> str:
    text = " ".join(places).lower()
    extra: list[str] = []
    for city in load_popular_cities():
        if any(alias in text for alias in city["aliases"]):
            extra.extend(city["aliases"])
    return f"{text} {' '.join(extra)}".strip()


def _near_label(places: list[str], keys: list[str]) -> str:
    for place in places:
        lowered = place.lower()
        if any(key in lowered for key in keys):
            return place
    return places[0] if places else ""


def _as_event(row: dict, near: str) -> dict:
    return {
        "name": row["name"],
        "kind": row["kind"],
        "city": row["city"],
        "region": row["region"],
        "country": row["country"],
        "when": row["when"],
        "day": "",
        "miles_from": 20,
        "near": near,
        "blurb": row["blurb"],
    }


def events_near(places: list[str], months: list[int] | int, limit: int) -> list[dict]:
    wanted = {months} if isinstance(months, int) else {int(item) for item in months if item}
    haystack = _haystack(places)
    found: list[dict] = []
    seen: set[str] = set()
    for row in load_popular_events():
        if not wanted.intersection(row["months"]):
            continue
        if haystack and not any(key in haystack for key in row["keys"]):
            continue
        if not haystack:
            continue
        name = row["name"]
        if name in seen:
            continue
        seen.add(name)
        found.append(_as_event(row, _near_label(places, row["keys"])))
        if len(found) >= limit:
            break
    return found


def catalog_prompt_lines(places: list[str], months: list[int] | int, limit: int = 12) -> str:
    items = events_near(places, months, limit)
    if not items:
        return ""
    lines = [
        "Known local moments near these places (include these; they are easy to miss):"
    ]
    for item in items:
        lines.append(
            f"- {item['name']} — {item['city']} — {item['when']} — {item['blurb']}"
        )
    return "\n".join(lines)


def months_for_horizon(horizon: str, today: date | None = None) -> list[int]:
    today = today or date.today()
    if horizon == "quarter":
        start = (today.month - 1) // 3 * 3 + 1
        return [start, start + 1, start + 2]
    return [today.month]


def attach_nearby_events(
    result: dict,
    places: list[str],
    months: list[int] | int,
    limit: int,
) -> dict:
    body = dict(result or {})
    existing = body.get("events")
    if isinstance(existing, list) and existing:
        body["places"] = body.get("places") or places
        return body
    body["events"] = events_near(places, months, limit)
    body["places"] = body.get("places") or places
    return body
