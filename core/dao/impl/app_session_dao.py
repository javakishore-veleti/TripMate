from datetime import datetime, timezone

from overrides import override

from adapters.persistence.engine import session_scope
from adapters.persistence.entities.app_session import AppSession
from core.dao.interfaces import AppSessionDao


class AppSessionDaoImpl(AppSessionDao):
    @override
    def create(self, token: str, user_id: str, expires_at: datetime) -> None:
        with session_scope() as session:
            session.add(AppSession(token=token, user_id=user_id, expires_at=expires_at))

    @override
    def get_valid(self, token: str) -> dict | None:
        with session_scope() as session:
            row = session.get(AppSession, token)
            if row is None or row.expires_at < datetime.now(timezone.utc):
                return None
            return {"token": row.token, "user_id": row.user_id, "expires_at": row.expires_at}

    @override
    def delete(self, token: str) -> None:
        with session_scope() as session:
            row = session.get(AppSession, token)
            if row is not None:
                session.delete(row)

    @override
    def delete_for_user(self, user_id: str) -> None:
        with session_scope() as session:
            session.query(AppSession).filter(AppSession.user_id == user_id).delete()
