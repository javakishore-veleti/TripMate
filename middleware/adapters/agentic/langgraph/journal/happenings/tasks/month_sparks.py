from middleware.common.popular_events import events_near


def sparks_near(places: list[str], month: int, limit: int) -> list[dict]:
    return events_near(places, month, limit)
