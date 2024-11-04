import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from test_app.db.dao import UserDAO
from test_app.db.models.users import User


@pytest.mark.anyio
async def test_register_201(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Tests user instance creation."""
    url = fastapi_app.url_path_for("register_user")
    test_username = "KamazNavoza"
    response = await client.post(
        url,
        json={
            "username": test_username,
            "password": "RulonOboev",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    dao = UserDAO(dbsession)

    instance = await dao.get_user_by_username(username=test_username)
    assert instance.username == test_username


@pytest.mark.anyio
async def test_register_400_user_already_exists(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    user: User,
) -> None:
    """Tests bad request when user with specific username is already exists."""
    url = fastapi_app.url_path_for("register_user")
    test_username = user.username
    response = await client.post(
        url,
        json={
            "username": test_username,
            "password": "RulonOboev",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
