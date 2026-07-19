"""RulePlanner: generates an initial task list by matching keywords in the goal."""

from ..models.project import Project
from ..models.task import Task
from ..tools.paper_result import PaperResult
from .planner import Planner
from .planner_result import PlannerResult

_DEFAULT_TASK_HOURS = 2.0

_KEYWORD_RULES: dict[str, list[str]] = {
    "paper": [
        "Read reviewer comments",
        "Revise methodology",
        "Update experiments",
        "Rewrite paper",
        "Final proofreading",
    ],
    "leetcode": [
        "Warm-up problems",
        "Medium problems",
        "Review mistakes",
    ],
}


class RulePlanner(Planner):
    """Matches keywords in ``project.goal`` against a fixed rule table."""

    def plan(self, project: Project, papers: list[PaperResult] | None = None) -> PlannerResult:
        goal = project.goal.lower()
        warnings: list[str] = []

        titles: list[str] = []
        for keyword, task_titles in _KEYWORD_RULES.items():
            if keyword in goal:
                titles.extend(task_titles)

        if not titles:
            warnings.append(f"No rule matched goal '{project.goal}'; no tasks were generated.")

        generated_tasks = [
            Task(
                id=f"{project.id}-task-{index}",
                title=title,
                estimated_time=_DEFAULT_TASK_HOURS,
            )
            for index, title in enumerate(titles, start=1)
        ]

        estimated_duration = (
            _DEFAULT_TASK_HOURS * len(generated_tasks) if generated_tasks else None
        )

        return PlannerResult(
            planner_name="RulePlanner",
            generated_tasks=generated_tasks,
            estimated_duration=estimated_duration,
            warnings=warnings,
        )
