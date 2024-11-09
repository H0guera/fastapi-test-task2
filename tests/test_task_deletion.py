import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from test_app.db.dao.task import TaskDAO
from test_app.db.models.tasks import Task
from test_app.db.models.users import User


@pytest.mark.anyio
async def test_delete_task_200_ok(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
    dbsession: AsyncSession,
    todo_task: Task,
) -> None:
    """Tests delete task 200 ok."""
    url = fastapi_app.url_path_for("delete_task", id=todo_task.id)

    response = await client.delete(
        url,
        headers=authenticated_headers.get("access_header"),
    )
    another_response = await client.delete(
        url,
        headers=authenticated_headers.get("access_header"),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert another_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_delete_task_403_for_not_owner(
    fastapi_app: FastAPI,
    client: AsyncClient,
    todo_task: Task,
    another_user: User,
    another_user_access_header: dict,
) -> None:
    """Tests 403 error for not owners."""
    url = fastapi_app.url_path_for("delete_task", id=todo_task.id)
    response = await client.patch(
        url,
        headers=another_user_access_header,
    )

    assert todo_task.user_id != another_user.id
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_delete_task_403_for_not_existing_task(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
    dbsession: AsyncSession,
    todo_task: Task,
    another_user: User,
    another_user_access_header: dict,
) -> None:
    """Tests 403 error for not existing task."""
    task_dao = TaskDAO(dbsession)
    broken_id = 999
    not_existing_task = await task_dao.get_task_by_id(broken_id)
    url = fastapi_app.url_path_for("delete_task", id=todo_task.id)

    response = await client.delete(
        url,
        headers=another_user_access_header,
    )

    assert not_existing_task is None
    assert response.status_code == status.HTTP_403_FORBIDDEN
