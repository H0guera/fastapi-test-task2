from pydantic import BaseModel

from test_app.utils.task_status import TaskStatus


class TaskBase(BaseModel):
    """Base tasks model."""

    title: str
    description: str
    status: TaskStatus
