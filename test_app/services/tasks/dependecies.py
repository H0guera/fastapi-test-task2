from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.params import Path
from starlette import status

from test_app.db.dao.task import TaskDAO
from test_app.db.models.tasks import Task
from test_app.db.models.users import User
from test_app.services.auth import get_current_auth_user


async def get_task_by_id(
    task_dao: Annotated[TaskDAO, Depends()],
    id: Annotated[int, Path],
    user: User = Depends(get_current_auth_user),
) -> Task:
    """Gets user's task (if exists) by id from url path or rais 403 http exception."""
    task = await task_dao.get_task_by_id(task_id=id)
    if task and task.user_id == user.id:
        return task
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
    )
