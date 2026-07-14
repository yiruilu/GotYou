"""Abstract Planner interface."""

from abc import ABC, abstractmethod

from ..models.project import Project
from .planner_result import PlannerResult


class Planner(ABC):
    @abstractmethod
    def plan(self, project: Project) -> PlannerResult:
        ...
