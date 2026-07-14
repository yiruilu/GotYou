"""PlannerResult: the output produced by a Planner."""

from dataclasses import dataclass, field

from ..models.task import Task


@dataclass
class PlannerResult:
    planner_name: str
    generated_tasks: list[Task] = field(default_factory=list)
    estimated_duration: float | None = None
    warnings: list[str] = field(default_factory=list)
