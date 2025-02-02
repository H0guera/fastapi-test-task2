from typing import TYPE_CHECKING, Sequence

from fastapi import Depends
from sqlalchemy import ScalarResult, select

from test_app.db.dependencies import get_db_session
from test_app.db.models.tasks import Task
from test_app.utils.task_status import TaskStatus
from test_app.web.api.tasks.schema import TaskBase, TaskUpdatePartial

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

    async def get_task_by_id(self, task_id: int) -> Task | None:
        """Gets task object by id."""
        stmt = select(Task).where(Task.id == task_id)
        return await self.session.scalar(stmt)

    async def get_all_tasks(
        self,
        status: TaskStatus | None,
    ) -> Sequence[Task]:
        """Gets all tasks with optional filter by status."""
        stmt = (
            select(Task)
            if status is None
            else select(Task).where(Task.status == status)
        )
        result: ScalarResult[Task] = await self.session.scalars(stmt)
        return list(result.all())

    async def update_task(
        self,
        target_task: Task,
        updated_task: TaskUpdatePartial,
        partial: bool = False,
    ) -> Task:
        """Updates task object."""
        for name, value in updated_task.model_dump(exclude_unset=partial).items():
            setattr(target_task, name, value)
        return target_task

    async def delete_task(self, task: Task) -> None:
        """Deletes task from db table."""
        return await self.session.delete(task)
