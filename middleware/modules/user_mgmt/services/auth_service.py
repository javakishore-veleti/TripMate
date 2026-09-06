from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from middleware.common.jwt_tokens import create_access_token, decode_access_token
from middleware.common.security import hash_password, verify_password
from middleware.common.user_preferences import empty_preferences, normalize_preferences
from middleware.core.dao.dao_names import DAO_APP_SESSION, DAO_APP_USER, DAO_TRAVEL_REQUEST
from middleware.core.dao.objects import DaoObjectFactory

SESSION_DAYS = 14


def _iso(value):
    return value.isoformat() if hasattr(value, "isoformat") else value


def public_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row.get("display_name") or "",
        "preferences": normalize_preferences(row.get("preferences")),
        "last_signin_at": _iso(row.get("last_signin_at")) if row.get("last_signin_at") else None,
    }


class AuthService:
    def __init__(self):
        self._users = DaoObjectFactory.get_dao(DAO_APP_USER)
        self._sessions = DaoObjectFactory.get_dao(DAO_APP_SESSION)
        self._requests = DaoObjectFactory.get_dao(DAO_TRAVEL_REQUEST)

    def signup(self, email: str, password: str, display_name: str = "") -> dict:
        cleaned_email = email.strip().lower()
        cleaned_password = password.strip()
        cleaned_name = display_name.strip() or cleaned_email.split("@")[0]
        if "@" not in cleaned_email or "." not in cleaned_email.split("@")[-1]:
            raise ValueError("Enter a valid email address.")
        if len(cleaned_password) < 8:
            raise ValueError("Password must be at least 8 characters.")
        if self._users.get_by_email(cleaned_email):
            raise ValueError("That email is already registered.")
        try:
            row = self._users.create(
                user_id=str(uuid4()),
                email=cleaned_email,
                password_hash=hash_password(cleaned_password),
                display_name=cleaned_name,
            )
        except IntegrityError as exc:
            raise ValueError("That email is already registered.") from exc
        stamped = self._users.record_signin(row["id"])
        return public_user(stamped or row)

    def signin(self, email: str, password: str) -> dict:
        row = self._users.get_by_email(email.strip().lower())
        if row is None or not verify_password(password, row["password_hash"]):
            raise ValueError("Email or password is incorrect.")
        stamped = self._users.record_signin(row["id"])
        return public_user(stamped or row)

    def create_session(self, user_id: str) -> str:
        token = uuid4().hex + uuid4().hex
        expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
        self._sessions.create(token=token, user_id=user_id, expires_at=expires_at)
        return token

    def issue_access_token(self, user: dict) -> str:
        return create_access_token(user["id"], user["email"])

    def user_from_access_token(self, token: str | None) -> dict | None:
        claims = decode_access_token(token)
        if claims is None:
            return None
        row = self._users.get_by_id(claims["sub"])
        return self._public_user(row) if row else None

    def user_from_token(self, token: str | None) -> dict | None:
        if not token:
            return None
        session = self._sessions.get_valid(token)
        if session is None:
            return None
        row = self._users.get_by_id(session["user_id"])
        return self._public_user(row) if row else None

    def _public_user(self, row: dict) -> dict:
        if row.get("last_signin_at"):
            return public_user(row)
        fallback = self._sessions.latest_created_at(row["id"])
        return public_user({**row, "last_signin_at": fallback or row.get("created_at")})

    def signout(self, token: str | None) -> None:
        if token:
            self._sessions.delete(token)

    def preferences_for(self, user_id: str) -> dict:
        row = self._users.get_by_id(user_id)
        if row is None:
            return empty_preferences()
        return normalize_preferences(row.get("preferences"))

    def save_preferences(self, user_id: str, preferences: dict) -> dict:
        current = self.preferences_for(user_id)
        incoming = preferences if isinstance(preferences, dict) else {}
        updated = self._users.update_preferences(
            user_id, normalize_preferences({**current, **incoming})
        )
        if updated is None:
            raise ValueError("User not found.")
        return self._public_user(updated)

    def delete_account(self, user_id: str) -> None:
        self._requests.delete_for_user(user_id)
        self._sessions.delete_for_user(user_id)
        if not self._users.delete(user_id):
            raise ValueError("User not found.")
