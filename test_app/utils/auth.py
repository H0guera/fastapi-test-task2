from typing import Any

import jwt

from test_app.settings import settings


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
