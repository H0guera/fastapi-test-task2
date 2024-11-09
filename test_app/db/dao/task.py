from typing import TYPE_CHECKING

from fastapi import Depends

from test_app.db.dependencies import get_db_session
from test_app.db.models.tasks import Task
from test_app.web.api.tasks.schema import TaskBase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class TaskDAO:
    """Class for accessing task table."""

    def __init__(
        self,
        session: "AsyncSession" = Depends(get_db_session),
    ) -> None:
        self.session = session

    async def create_task_model(
        self,
        create_task: TaskBase,
        user_id: int,
    ) -> Task:
        """Adds single task model to session."""
        task = Task(
            title=create_task.title,
            description=create_task.description,
            status=create_task.status,
            user_id=user_id,
        )
        self.session.add(task)
        return task
