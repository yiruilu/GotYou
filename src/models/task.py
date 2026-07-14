"""Task model: a single unit of work within a Project."""

from dataclasses import dataclass, field
from datetime import date

from .enums import Priority, TaskStatus


@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    estimated_time: float | None = None
    due_date: date | None = None
    dependencies: list[str] = field(default_factory=list)
