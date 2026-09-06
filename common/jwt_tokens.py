import os
from datetime import datetime, timedelta, timezone

import jwt

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 14
_LOCAL_DEV_SECRET = "your-next-travel-local-dev-only"


def jwt_secret() -> str:
    return os.getenv("JWT_SECRET", "").strip() or _LOCAL_DEV_SECRET


def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=JWT_EXPIRE_DAYS)).timestamp()),
    }
    return jwt.encode(payload, jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_access_token(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        claims = jwt.decode(token, jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    user_id = str(claims.get("sub") or "").strip()
    if not user_id:
        return None
    return {"sub": user_id, "email": str(claims.get("email") or "")}
