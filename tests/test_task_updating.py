import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from test_app.db.dao.task import TaskDAO
from test_app.db.models.tasks import Task
from test_app.db.models.users import User
from test_app.utils.task_status import TaskStatus
from test_app.web.api.tasks.schema import TaskUpdatePartial


@pytest.mark.anyio
async def test_partial_update_task_200(
    fastapi_app: FastAPI,
    client: AsyncClient,
    authenticated_headers: dict,
    dbsession: AsyncSession,
    user: User,
    todo_task: Task,
) -> None:
    """Tests partial updating tasks 200 ok."""
    url = fastapi_app.url_path_for("task_update_partial", id=todo_task.id)
    new_title = todo_task.title + "_new"
    new_status = TaskStatus.IN_PROGRESS.value
    updated_task = TaskUpdatePartial(
        title=new_title,
        status=new_status,
    )

    response = await client.patch(
        url,
        json=updated_task.model_dump(),
        headers=authenticated_headers.get("access_header"),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("title") == new_title
    assert response.json().get("status") == new_status


@pytest.mark.anyio
async def test_partial_update_task_403_for_not_owner(
    fastapi_app: FastAPI,
    client: AsyncClient,
    dbsession: AsyncSession,
    todo_task: Task,
    another_user: User,
    another_user_access_header: dict,
) -> None:
    """Tests 403 error for not owners."""
    url = fastapi_app.url_path_for("task_update_partial", id=todo_task.id)
    updated_task = TaskUpdatePartial(
        title=todo_task.title + "_new",
        description=todo_task.description + "_new",
        status=TaskStatus.IN_PROGRESS,
    )

    response = await client.patch(
        url,
        json=updated_task.model_dump(),
        headers=another_user_access_header,
    )

    assert todo_task.user_id != another_user.id
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_partial_update_task_403_for_not_existing_task(
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
    url = fastapi_app.url_path_for("task_update_partial", id=broken_id)
    updated_task = TaskUpdatePartial(
        title="_new",
        description="_new",
        status=TaskStatus.IN_PROGRESS,
    )

    response = await client.patch(
        url,
        json=updated_task.model_dump(),
        headers=another_user_access_header,
    )

    assert not_existing_task is None
    assert response.status_code == status.HTTP_403_FORBIDDEN
