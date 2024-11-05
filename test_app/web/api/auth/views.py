from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, status
from fastapi.param_functions import Depends

from test_app.db.dao import UserDAO
from test_app.db.models.users import User
from test_app.utils.auth import create_access_token, create_refresh_token
from test_app.web.api.auth.schema import TokenInfo, UserBase, UserCreate
from test_app.web.api.exceptions import UserAlreadyExistsError

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserBase,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "content": {
                "application/json": {
                    "examples": {
                        "REGISTER_USER_ALREADY_EXISTS": {
                            "summary": "A user with this username already exists.",
                            "value": {
                                "detail": "REGISTER_USER_ALREADY_EXISTS",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def register_user(
    new_user_object: UserCreate,
    user_dao: Annotated[UserDAO, Depends()],
) -> User | None:
    """
    Creates user model in the database.

    :param new_user_object: new user model item.
    :param user_dao: DAO for user models.
    """
    try:
        new_user = await user_dao.create_user_model(user_create=new_user_object)  # type: ignore[attr-defined]
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REGISTER_USER_ALREADY_EXISTS",
        ) from e
    return new_user


@router.post("/login", response_model=TokenInfo)
async def login_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    user_dao: Annotated[UserDAO, Depends()],
) -> TokenInfo:
    """Authenticates user by username.Saves refresh token to redis."""
    user = await user_dao.authenticate(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LOGIN_BAD_CREDENTIALS",
        )
    access_token = create_access_token({"sub": user.id, "username": user.username})
    refresh_token = create_refresh_token({"sub": user.id})
    await user_dao.save_refresh_token_to_redis(user=user, token=refresh_token)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)
