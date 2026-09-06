PIPELINE_DASHBOARD = "dashboard"
PIPELINE_JOURNAL = "journal"
PIPELINE_PLAN = "plan"
PIPELINE_PREFERENCES = "preferences"
PIPELINE_ACCOUNT = "account"

CHANGE_THRESHOLD = 0.05


def dashboard_pipeline_key(horizon: str) -> str:
    name = (horizon or "month").strip().lower()
    if name not in {"week", "month", "quarter"}:
        name = "month"
    return f"{PIPELINE_DASHBOARD}:{name}"
