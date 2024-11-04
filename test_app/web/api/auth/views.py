from typing import Annotated

from fastapi import APIRouter, HTTPException, status
from fastapi.param_functions import Depends

from test_app.db.dao import UserDAO
from test_app.db.models.users import User
from test_app.web.api.auth.schema import UserBase, UserCreate
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
