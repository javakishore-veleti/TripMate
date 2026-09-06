import json
from difflib import SequenceMatcher
from typing import Callable

from overrides import override

from middleware.common.pipeline_keys import CHANGE_THRESHOLD
from middleware.modules.shared.persistence.dao.dao_names import DAO_PIPELINE_SNAPSHOT
from middleware.modules.shared.persistence.dao.objects import DaoObjectFactory
from middleware.modules.shared.persistence.interfaces import PipelineSnapshotDao
from middleware.modules.shared.services.interfaces import PipelineCacheService


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, default=str, separators=(",", ":"))


def change_ratio(left, right) -> float:
    if left == right:
        return 0.0
    return 1.0 - SequenceMatcher(None, _canonical(left), _canonical(right)).ratio()


def _usable_cache(stored: dict) -> bool:
    if stored.get("needs_model") and not stored.get("events"):
        return False
    if "events" in stored and not stored.get("events"):
        return False
    return True


def _with_meta(payload: dict, snapshot: dict, cached: bool) -> dict:
    body = dict(payload or {})
    body["cached"] = cached
    body["checked_at"] = snapshot.get("checked_at")
    body["updated_at"] = snapshot.get("updated_at")
    return body


class PipelineCacheServiceImpl(PipelineCacheService):
    def __init__(self, dao: PipelineSnapshotDao | None = None):
        self._dao: PipelineSnapshotDao = dao or DaoObjectFactory.get_dao(DAO_PIPELINE_SNAPSHOT)

    @override
    def remember(
        self,
        user_id: str,
        pipeline_key: str,
        context: dict,
        produce: Callable[[], dict],
    ) -> dict:
        snapshot = self._dao.get_for_user(user_id, pipeline_key)
        stored = (snapshot or {}).get("payload_json") or {}
        if (
            snapshot
            and change_ratio(snapshot.get("context_json") or {}, context) < CHANGE_THRESHOLD
            and _usable_cache(stored)
        ):
            return _with_meta(stored, snapshot, cached=True)

        payload = produce() or {}
        stored_payload = (snapshot or {}).get("payload_json") or {}
        if snapshot and change_ratio(stored_payload, payload) < CHANGE_THRESHOLD:
            kept = self._dao.upsert(
                {
                    "user_id": user_id,
                    "pipeline_key": pipeline_key,
                    "context_json": context,
                    "payload_json": stored_payload,
                }
            )
            return _with_meta(stored_payload, kept, cached=True)

        saved = self._dao.upsert(
            {
                "user_id": user_id,
                "pipeline_key": pipeline_key,
                "context_json": context,
                "payload_json": payload,
            }
        )
        return _with_meta(payload, saved, cached=False)
