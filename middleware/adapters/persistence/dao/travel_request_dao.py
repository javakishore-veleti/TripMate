from datetime import datetime, timezone
from uuid import uuid4

from overrides import override

from middleware.adapters.persistence.engine import session_scope
from middleware.adapters.persistence.entities.travel_request import TravelRequestRecord
from middleware.core.dao.interfaces import TravelRequestDao


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _to_dict(row: TravelRequestRecord) -> dict:
    return {
        "id": row.id,
        "thread_id": row.thread_id,
        "user_id": row.user_id,
        "prompt": row.prompt,
        "status": row.status,
        "agentic_adapter": row.agentic_adapter,
        "llm_provider": row.llm_provider,
        "llm_model": row.llm_model,
        "result": row.result or {},
        "hitl": row.hitl or {},
        "usage": row.usage or {},
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


class TravelRequestDaoImpl(TravelRequestDao):
    @override
    def upsert(self, record: dict) -> dict:
        now = datetime.now(timezone.utc)
        with session_scope() as session:
            row = (
                session.query(TravelRequestRecord)
                .filter(TravelRequestRecord.thread_id == record["thread_id"])
                .one_or_none()
            )
            if row is None:
                row = TravelRequestRecord(
                    id=record.get("id") or str(uuid4()),
                    thread_id=record["thread_id"],
                    user_id=record["user_id"],
                    prompt=record.get("prompt") or "",
                    created_at=now,
                )
                session.add(row)
            row.prompt = record.get("prompt") or row.prompt
            row.status = record["status"]
            row.agentic_adapter = record["agentic_adapter"]
            row.llm_provider = record["llm_provider"]
            row.llm_model = record["llm_model"]
            row.result = record.get("result") or {}
            row.hitl = record.get("hitl") or {}
            row.usage = record.get("usage") or {}
            row.updated_at = now
            session.flush()
            return _to_dict(row)

    @override
    def list_for_user(self, user_id: str) -> list[dict]:
        with session_scope() as session:
            rows = (
                session.query(TravelRequestRecord)
                .filter(TravelRequestRecord.user_id == user_id)
                .order_by(TravelRequestRecord.updated_at.desc())
                .all()
            )
            return [_to_dict(row) for row in rows]

    @override
    def get_for_user(self, user_id: str, thread_id: str) -> dict | None:
        with session_scope() as session:
            row = (
                session.query(TravelRequestRecord)
                .filter(
                    TravelRequestRecord.user_id == user_id,
                    TravelRequestRecord.thread_id == thread_id,
                )
                .one_or_none()
            )
            return _to_dict(row) if row else None

    @override
    def delete_for_user(self, user_id: str) -> None:
        with session_scope() as session:
            session.query(TravelRequestRecord).filter(
                TravelRequestRecord.user_id == user_id
            ).delete()

    @override
    def delete_for_user_thread(self, user_id: str, thread_id: str) -> bool:
        with session_scope() as session:
            deleted = (
                session.query(TravelRequestRecord)
                .filter(
                    TravelRequestRecord.user_id == user_id,
                    TravelRequestRecord.thread_id == thread_id,
                )
                .delete()
            )
            return bool(deleted)
