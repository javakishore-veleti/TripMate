from calendar import monthrange
from datetime import date, timedelta


def window_for(horizon: str, today: date | None = None) -> tuple[date, date, str]:
    today = today or date.today()
    if horizon == "week":
        end = today + timedelta(days=6)
        return today, end, f"this week ({today.isoformat()} to {end.isoformat()})"
    if horizon == "quarter":
        start_month = (today.month - 1) // 3 * 3 + 1
        start = date(today.year, start_month, 1)
        end_month = start_month + 2
        end = date(today.year, end_month, monthrange(today.year, end_month)[1])
        quarter = (start_month - 1) // 3 + 1
        return start, end, f"this quarter Q{quarter} {today.year} ({start.isoformat()} to {end.isoformat()})"
    start = date(today.year, today.month, 1)
    end = date(today.year, today.month, monthrange(today.year, today.month)[1])
    return start, end, f"this month ({start.strftime('%B %Y')}, {start.isoformat()} to {end.isoformat()})"


def clean_event(raw: dict, near: str) -> dict | None:
    name = str(raw.get("name") or "").strip()
    if not name:
        return None
    kind = str(raw.get("kind") or "culture").strip().lower()
    if kind not in {"festival", "culture", "season", "community"}:
        kind = "culture"
    try:
        miles = int(raw.get("miles_from") or raw.get("miles") or 0)
    except (TypeError, ValueError):
        miles = 0
    return {
        "name": name,
        "kind": kind,
        "city": str(raw.get("city") or "").strip(),
        "region": str(raw.get("region") or raw.get("state") or "").strip(),
        "country": str(raw.get("country") or "").strip(),
        "when": str(raw.get("when") or "").strip(),
        "day": str(raw.get("day") or "").strip(),
        "miles_from": max(0, miles),
        "near": str(raw.get("near") or near).strip(),
        "blurb": str(raw.get("blurb") or "").strip(),
    }
