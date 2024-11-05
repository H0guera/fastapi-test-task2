from datetime import datetime, timedelta
from typing import Any

import jwt

from test_app.settings import settings

JWT_TYPE_FIELD = "type"
ACCESS_JWT_TYPE = "access"
REFRESH_JWT_TYPE = "refresh"


def encode_jwt(
    payload: dict[str, Any],
    key: str = settings.auth_jwt.users_secret,
    algorithm: str = settings.auth_jwt.algorithm,
) -> str:
    """Creates jwt token."""
    return jwt.encode(
        payload,
        key,
        algorithm,
    )


def decode_jwt(
    token: str | bytes,
    key: str = settings.auth_jwt.users_secret,
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict[str, Any]:
    """Decodes jwt token."""
    return jwt.decode(
        token,
        key,
        algorithms=[algorithm],
    )


def create_jwt(token_type: str, payload: dict[str, Any]) -> str:
    """Adds type of token to payload and write token."""
    payload.update({JWT_TYPE_FIELD: token_type})
    return encode_jwt(payload=payload)


def create_access_token(
    token_data: dict[str, Any],
    expire_minutes: int | None = settings.auth_jwt.access_token_expire_minutes,
) -> str:
    """Adds exp to payload and creates access token."""
    now = datetime.utcnow()
    if expire_minutes:
        token_data.update(
            exp=now + timedelta(minutes=expire_minutes),
        )
    return create_jwt(token_type=ACCESS_JWT_TYPE, payload=token_data)


def create_refresh_token(token_data: dict[str, Any]) -> str:
    """Creates refresh token."""
    token_data.update(iat=datetime.utcnow())
    return create_jwt(token_type=REFRESH_JWT_TYPE, payload=token_data)
