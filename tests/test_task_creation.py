import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


@pytest.mark.anyio
async def test_task_creation_201(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    authenticated_headers: dict,
) -> None:
    """Tests user instance creation 201 ok."""
    url = fastapi_app.url_path_for("create_task")
    response = await client.post(
        url,
        json={
            "title": "JaloDrakona",
            "description": "OchenOpasno",
            "status": "TODO",
        },
        headers=authenticated_headers.get("access_header"),
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_task_creation_403(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    authenticated_headers: dict,
) -> None:
    """Tests user instance creation 403 error."""
    url = fastapi_app.url_path_for("create_task")
    response = await client.post(
        url,
        json={
            "title": "JaloDrakona",
            "description": "OchenOpasno",
            "status": "TODO",
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_task_creation_401(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    authenticated_headers: dict,
) -> None:
    """Tests user instance creation 401 error."""
    url = fastapi_app.url_path_for("create_task")
    invalid_headers = [
        {"Authorization": "Bearer UshelZaHlebom"},
        authenticated_headers.get("refresh_header"),
    ]

    for invalid_header in invalid_headers:
        response = await client.post(
            url,
            json={
                "title": "JaloDrakona",
                "description": "OchenOpasno",
                "status": "TODO",
            },
            headers=invalid_header,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
