from pydantic import BaseModel

from test_app.utils.task_status import TaskStatus


class TaskBase(BaseModel):
    """Base tasks model."""

    title: str
    description: str
    status: TaskStatus


class TaskUpdatePartial(BaseModel):
    """Model for optional update task object."""

    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
