from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from common.jwt_tokens import create_access_token, decode_access_token
from common.security import hash_password, verify_password
from common.user_preferences import empty_preferences, normalize_preferences
from core.dao.dao_names import DAO_APP_SESSION, DAO_APP_USER, DAO_TRAVEL_REQUEST
from core.dao.objects import DaoObjectFactory

SESSION_DAYS = 14


def public_user(row: dict) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "display_name": row.get("display_name") or "",
        "preferences": normalize_preferences(row.get("preferences")),
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
        return public_user(row)

    def signin(self, email: str, password: str) -> dict:
        row = self._users.get_by_email(email.strip().lower())
        if row is None or not verify_password(password, row["password_hash"]):
            raise ValueError("Email or password is incorrect.")
        return public_user(row)

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
        return public_user(row) if row else None

    def user_from_token(self, token: str | None) -> dict | None:
        if not token:
            return None
        session = self._sessions.get_valid(token)
        if session is None:
            return None
        row = self._users.get_by_id(session["user_id"])
        return public_user(row) if row else None

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
        return public_user(updated)

    def delete_account(self, user_id: str) -> None:
        self._requests.delete_for_user(user_id)
        self._sessions.delete_for_user(user_id)
        if not self._users.delete(user_id):
            raise ValueError("User not found.")
