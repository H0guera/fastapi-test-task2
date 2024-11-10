from asyncio import sleep

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette import status

from test_app.db.models.users import User
from test_app.utils.auth import create_refresh_token


@pytest.mark.anyio
async def test_refresh_200(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
) -> None:
    """Tests 'auth/refresh' 200 ok."""
    url = fastapi_app.url_path_for("token_refresh")

    response = await client.post(
        url,
        headers=authenticated_headers.get("refresh_header"),
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_refresh_403(
    fastapi_app: FastAPI,
    client: AsyncClient,
) -> None:
    """Tests 'auth/refresh' 403 error."""
    url = fastapi_app.url_path_for("token_refresh")

    response = await client.post(url)
    wrong_header_response = await client.post(
        url,
        headers={"Authorization": "UshelZaHlebom"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert wrong_header_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_refresh_401_invalid_token(
    fastapi_app: FastAPI,
    client: AsyncClient,
    user: User,
    authenticated_headers: dict,
) -> None:
    """Tests 'auth/refresh' 401 error."""
    url = fastapi_app.url_path_for("token_refresh")
    # for make sure we are creating fresh refresh token not in redis
    await sleep(1)
    fresh_refresh_token = create_refresh_token({"sub": user.id})
    invalid_headers = [
        {"Authorization": "Bearer UshelZaHlebom"},
        authenticated_headers.get("access_header"),
        {"Authorization": f"Bearer {fresh_refresh_token}"},
    ]

    for header in invalid_headers:
        response = await client.post(url, headers=header)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
