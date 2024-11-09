from typing import Annotated, Sequence

from fastapi import APIRouter
from fastapi import status as http_status
from fastapi.param_functions import Depends

from test_app.db.dao.task import TaskDAO
from test_app.db.models.tasks import Task
from test_app.db.models.users import User
from test_app.services.auth import get_current_auth_user
from test_app.services.tasks.dependecies import get_task_by_id
from test_app.utils.task_status import TaskStatus
from test_app.web.api.tasks.schema import TaskBase, TaskUpdatePartial

router = APIRouter()


@router.post(
    "/",
    status_code=http_status.HTTP_201_CREATED,
    response_model=TaskBase,
    responses={
        http_status.HTTP_401_UNAUTHORIZED: {
            "content": {
                "application/json": {
                    "examples": {
                        "UNAUTHORIZED": {
                            "summary": "Unauthorized.",
                            "value": {
                                "detail": "UNAUTHORIZED",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def create_task(
    new_task_object: TaskBase,
    task_dao: Annotated[TaskDAO, Depends()],
    user: User = Depends(get_current_auth_user),
) -> Task:
    """Creates task."""
    return await task_dao.create_task_model(
        create_task=new_task_object,
        user_id=user.id,
    )


@router.get(
    "/",
    response_model=list[TaskBase],
    responses={
        http_status.HTTP_401_UNAUTHORIZED: {
            "content": {
                "application/json": {
                    "examples": {
                        "UNAUTHORIZED": {
                            "summary": "Unauthorized.",
                            "value": {
                                "detail": "UNAUTHORIZED",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def get_all_tasks(
    task_dao: Annotated[TaskDAO, Depends()],
    status: TaskStatus | None = None,
    user: User = Depends(get_current_auth_user),
) -> Sequence[Task]:
    """Gets all tasks with optional filter by status."""
    return await task_dao.get_all_tasks(status=status)


@router.patch(
    "/{id}",
    response_model=TaskUpdatePartial,
    response_model_exclude_unset=True,
    responses={
        http_status.HTTP_403_FORBIDDEN: {
            "content": {
                "application/json": {
                    "examples": {
                        "FORBIDDEN": {
                            "summary": "Forbidden.",
                            "value": {
                                "detail": "Forbidden",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def task_update_partial(
    updated_task: TaskUpdatePartial,
    task_dao: Annotated[TaskDAO, Depends()],
    task: Task = Depends(get_task_by_id),
) -> Task:
    """Partial updates task."""
    return await task_dao.update_task(
        target_task=task,
        updated_task=updated_task,
        partial=True,
    )


@router.delete(
    "/{id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
    responses={
        http_status.HTTP_403_FORBIDDEN: {
            "content": {
                "application/json": {
                    "examples": {
                        "FORBIDDEN": {
                            "summary": "Forbidden.",
                            "value": {
                                "detail": "Forbidden",
                            },
                        },
                    },
                },
            },
        },
    },
)
async def delete_task(
    task_dao: Annotated[TaskDAO, Depends()],
    task: Task = Depends(get_task_by_id),
) -> None:
    """Deletes task."""
    return await task_dao.delete_task(task=task)
