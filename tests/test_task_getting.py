import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from test_app.db.dao.task import TaskDAO
from test_app.db.models.tasks import Task
from test_app.utils.task_status import TaskStatus


@pytest.mark.anyio
async def test_get_all_tasks_200(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
    dbsession: AsyncSession,
) -> None:
    """Tests getting all tasks without status filter."""
    url = fastapi_app.url_path_for("get_all_tasks")
    task_dao = TaskDAO(dbsession)

    response = await client.get(
        url,
        headers=authenticated_headers.get("access_header"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(await task_dao.get_all_tasks(status=None))


@pytest.mark.anyio
async def test_get_all_todo_tasks(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
    dbsession: AsyncSession,
    todo_task: Task,
    done_task: Task,
) -> None:
    """Tests getting all tasks with query status filter."""
    url = fastapi_app.url_path_for("get_all_tasks")
    task_dao = TaskDAO(dbsession)
    todo_task_status = TaskStatus.TODO.value

    response = await client.get(
        url,
        params={"status": todo_task_status},
        headers=authenticated_headers.get("access_header"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(
        await task_dao.get_all_tasks(status=todo_task_status),
    )
    for task in response.json():
        assert task.get("status") == todo_task_status


@pytest.mark.anyio
async def test_get_all_tasks_401(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
) -> None:
    """Tests getting 401 error with bad auth bearer tokens."""
    url = fastapi_app.url_path_for("get_all_tasks")
    invalid_headers = [
        {"Authorization": "Bearer UshelZaHlebom"},
        authenticated_headers.get("refresh_header"),
    ]

    for header in invalid_headers:
        response = await client.get(
            url,
            headers=header,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_get_all_tasks_403(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
) -> None:
    """Tests getting 403 error without auth bearer token."""
    url = fastapi_app.url_path_for("get_all_tasks")

    response = await client.get(
        url,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
