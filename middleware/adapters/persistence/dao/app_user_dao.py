from datetime import datetime, timezone

from overrides import override

from middleware.adapters.persistence.engine import session_scope
from middleware.adapters.persistence.entities.app_user import AppUser
from middleware.core.dao.interfaces import AppUserDao


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def _to_dict(user: AppUser) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "password_hash": user.password_hash,
        "preferences": user.preferences or {},
        "created_at": _iso(user.created_at),
        "last_signin_at": _iso(user.last_signin_at),
    }


class AppUserDaoImpl(AppUserDao):
    @override
    def create(self, user_id: str, email: str, password_hash: str, display_name: str) -> dict:
        with session_scope() as session:
            user = AppUser(
                id=user_id,
                email=email,
                password_hash=password_hash,
                display_name=display_name,
            )
            session.add(user)
            session.flush()
            return _to_dict(user)

    @override
    def get_by_email(self, email: str) -> dict | None:
        with session_scope() as session:
            user = session.query(AppUser).filter(AppUser.email == email).one_or_none()
            return _to_dict(user) if user else None

    @override
    def get_by_id(self, user_id: str) -> dict | None:
        with session_scope() as session:
            user = session.get(AppUser, user_id)
            return _to_dict(user) if user else None

    @override
    def update_preferences(self, user_id: str, preferences: dict) -> dict | None:
        with session_scope() as session:
            user = session.get(AppUser, user_id)
            if user is None:
                return None
            user.preferences = preferences
            session.flush()
            return _to_dict(user)

    @override
    def record_signin(self, user_id: str) -> dict | None:
        with session_scope() as session:
            user = session.get(AppUser, user_id)
            if user is None:
                return None
            user.last_signin_at = datetime.now(timezone.utc)
            session.flush()
            return _to_dict(user)

    @override
    def delete(self, user_id: str) -> bool:
        with session_scope() as session:
            user = session.get(AppUser, user_id)
            if user is None:
                return False
            session.delete(user)
            return True
