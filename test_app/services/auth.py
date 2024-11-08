from typing import Annotated

from fastapi import HTTPException
from fastapi.param_functions import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette import status

from test_app.db.dao import UserDAO
from test_app.db.models.users import User
from test_app.utils.auth import (
    ACCESS_JWT_TYPE,
    REFRESH_JWT_TYPE,
    create_access_token,
)

http_bearer = HTTPBearer()


async def get_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
) -> str:
    """Returns bearer token from Authorization header."""
    return credentials.credentials


async def get_current_auth_user(
    user_dao: Annotated[UserDAO, Depends()],
    token: str = Depends(get_bearer_token),
) -> User:
    """Getting current authenticated user by access token."""
    user = await user_dao.get_current_auth_user_by_token(
        token,
        expected_token_type=ACCESS_JWT_TYPE,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )
    return user


async def get_current_auth_user_by_refresh_token(
    user_dao: Annotated[UserDAO, Depends()],
    token: str = Depends(get_bearer_token),
) -> User:
    """Getting current authenticated user by refresh token."""
    user = await user_dao.get_current_auth_user_by_token(
        token,
        expected_token_type=REFRESH_JWT_TYPE,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )
    return user


async def refresh_access_token(
    user: User = Depends(get_current_auth_user_by_refresh_token),
) -> str:
    """Refreshes access token by bearer refresh token from Authorization header."""
    return create_access_token({"sub": user.id, "username": user.username})
