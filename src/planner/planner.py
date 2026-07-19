"""Abstract Planner interface."""

from abc import ABC, abstractmethod

from ..models.project import Project
from ..tools.paper_result import PaperResult
from .planner_result import PlannerResult


class Planner(ABC):
    @abstractmethod
    def plan(self, project: Project, papers: list[PaperResult] | None = None) -> PlannerResult:
        ...
