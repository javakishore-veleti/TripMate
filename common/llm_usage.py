from contextvars import ContextVar

_usage: ContextVar[dict | None] = ContextVar("llm_usage", default=None)


def start_usage() -> dict:
    bucket = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
        "llm_calls": 0,
    }
    _usage.set(bucket)
    return bucket


def add_usage(input_tokens: int = 0, output_tokens: int = 0, cost_usd: float | None = None) -> None:
    bucket = _usage.get()
    if bucket is None:
        return
    bucket["input_tokens"] += int(input_tokens or 0)
    bucket["output_tokens"] += int(output_tokens or 0)
    bucket["llm_calls"] += 1
    if cost_usd is not None:
        bucket["cost_usd"] = round(float(bucket["cost_usd"]) + float(cost_usd), 8)


def get_usage() -> dict:
    return dict(_usage.get() or {})
