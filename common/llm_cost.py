import json
from functools import lru_cache
from pathlib import Path

_COST_FILE = Path(__file__).resolve().parent.parent / "llms_cost.json"


@lru_cache(maxsize=1)
def _model_rates() -> dict:
    if not _COST_FILE.is_file():
        return {}
    payload = json.loads(_COST_FILE.read_text(encoding="utf-8"))
    models = payload.get("models") or {}
    return models if isinstance(models, dict) else {}


def model_entries() -> dict:
    return dict(_model_rates())


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float | None:
    rates = _model_rates().get(model) or _model_rates().get(model.split("/")[-1])
    if not isinstance(rates, dict):
        return None
    input_rate = rates.get("input")
    output_rate = rates.get("output")
    if input_rate is None or output_rate is None:
        return None
    cost = (input_tokens / 1_000_000) * float(input_rate) + (
        output_tokens / 1_000_000
    ) * float(output_rate)
    return round(cost, 8)
