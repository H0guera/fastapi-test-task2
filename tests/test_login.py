import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from test_app.db.models.users import User
from tests.conftest import USER_PASSWORD


@pytest.mark.anyio
async def test_login_200(
    fastapi_app: FastAPI,
    client: AsyncClient,
    user: User,
    dbsession: AsyncSession,
) -> None:
    """Tests login 200 ok."""
    url = fastapi_app.url_path_for("login_user")
    username = user.username
    password = USER_PASSWORD

    response = await client.post(
        url,
        data={"username": username, "password": password},
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_login_400(
    fastapi_app: FastAPI,
    client: AsyncClient,
    user: User,
    dbsession: AsyncSession,
) -> None:
    """Tests login wrong credentials 400 error."""
    url = fastapi_app.url_path_for("login_user")
    username = user.username
    password = USER_PASSWORD

    response = await client.post(
        url,
        data={"username": username + "wrong", "password": password},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = await client.post(
        url,
        data={"username": username, "password": password + "wrong"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
