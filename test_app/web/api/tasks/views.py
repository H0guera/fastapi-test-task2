from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi import status as http_status
from fastapi.param_functions import Depends

from test_app.db.dao.task import TaskDAO
from test_app.db.models.tasks import Task
from test_app.db.models.users import User
from test_app.services.auth import get_current_auth_user
from test_app.web.api.tasks.schema import TaskBase

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
    user: User | None = Depends(get_current_auth_user),
) -> Task:
    """Creates task."""
    if user is None:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="UNAUTHORIZED",
        )
    return await task_dao.create_task_model(
        create_task=new_task_object,
        user_id=user.id,
    )
