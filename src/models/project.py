"""Project model: the top-level container for a user's academic goal."""

from dataclasses import dataclass, field
from datetime import date

from .feedback import Feedback
from .progress import Progress
from .resource import Resource
from .task import Task


@dataclass
class Project:
    id: str
    title: str
    goal: str
    deadline: date | None = None
    tasks: list[Task] = field(default_factory=list)
    resources: list[Resource] = field(default_factory=list)
    feedback: list[Feedback] = field(default_factory=list)
    progress: Progress | None = None
    notes: str = ""
