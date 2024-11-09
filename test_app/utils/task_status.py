from enum import Enum


class TaskStatus(str, Enum):
    """Available statuses of task."""

    TODO = "TODO"
    IN_PROGRESS = "InProgress"
    DONE = "Done"
