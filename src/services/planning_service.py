"""PlanningService: orchestrates a Planner and applies its output to a Project."""

from dataclasses import replace

from ..models.project import Project
from ..planner.planner import Planner
from ..planner.planner_result import PlannerResult
from ..tools.paper_result import PaperResult


class PlanningService:
    """Runs a Planner against a Project and, optionally, merges the result in."""

    def __init__(self, planner: Planner):
        self._planner = planner

    def generate_plan(self, project: Project, papers: list[PaperResult] | None = None) -> PlannerResult:
        return self._planner.plan(project, papers=papers)

    def apply_plan(self, project: Project, result: PlannerResult) -> Project:
        """Returns a new Project with the planner's tasks appended.

        Never mutates `project` in place, for the same reason Planner never
        does: a plan is a proposal, not a foregone update.
        """
        return replace(project, tasks=[*project.tasks, *result.generated_tasks])
