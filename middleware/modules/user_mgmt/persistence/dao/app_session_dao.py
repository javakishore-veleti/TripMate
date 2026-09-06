from datetime import datetime, timezone

from overrides import override

from middleware.persistence.engine import session_scope
from middleware.modules.user_mgmt.persistence.entities.app_session import AppSession
from middleware.modules.user_mgmt.persistence.interfaces import AppSessionDao


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

    @override
    def latest_created_at(self, user_id: str) -> datetime | None:
        with session_scope() as session:
            row = (
                session.query(AppSession)
                .filter(AppSession.user_id == user_id)
                .order_by(AppSession.created_at.desc())
                .first()
            )
            return row.created_at if row else None
