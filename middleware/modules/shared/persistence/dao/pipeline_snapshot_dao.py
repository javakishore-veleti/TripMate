from datetime import datetime, timezone
from uuid import uuid4

from overrides import override

from middleware.modules.shared.persistence.entities.pipeline_snapshot import PipelineSnapshot
from middleware.modules.shared.persistence.interfaces import PipelineSnapshotDao
from middleware.persistence.engine import session_scope


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _to_dict(row: PipelineSnapshot) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "pipeline_key": row.pipeline_key,
        "context_json": row.context_json or {},
        "payload_json": row.payload_json or {},
        "checked_at": _iso(row.checked_at),
        "updated_at": _iso(row.updated_at),
    }


class PipelineSnapshotDaoImpl(PipelineSnapshotDao):
    @override
    def get_for_user(self, user_id: str, pipeline_key: str) -> dict | None:
        with session_scope() as session:
            row = (
                session.query(PipelineSnapshot)
                .filter(
                    PipelineSnapshot.user_id == user_id,
                    PipelineSnapshot.pipeline_key == pipeline_key,
                )
                .one_or_none()
            )
            return _to_dict(row) if row else None

    @override
    def upsert(self, record: dict) -> dict:
        now = datetime.now(timezone.utc)
        with session_scope() as session:
            row = (
                session.query(PipelineSnapshot)
                .filter(
                    PipelineSnapshot.user_id == record["user_id"],
                    PipelineSnapshot.pipeline_key == record["pipeline_key"],
                )
                .one_or_none()
            )
            if row is None:
                row = PipelineSnapshot(
                    id=record.get("id") or str(uuid4()),
                    user_id=record["user_id"],
                    pipeline_key=record["pipeline_key"],
                )
                session.add(row)
            row.context_json = record.get("context_json") or {}
            row.payload_json = record.get("payload_json") or {}
            row.checked_at = now
            row.updated_at = now
            session.flush()
            return _to_dict(row)
