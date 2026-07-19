"""Rule-based review of a PlannerResult, used by the review_plan node.

Deliberately simple: fixed, readable checks rather than a scored/weighted
rubric. Each rule inspects `PlannerResult` alone (no network/LLM calls), so
review_plan stays fast and deterministic.
"""

from dataclasses import dataclass

from ..planner.planner_result import PlannerResult


@dataclass
class ReviewResult:
    passed: bool
    notes: list[str]


def review_plan_rules(plan: PlannerResult) -> ReviewResult:
    """Check a generated plan against a few basic quality rules."""
    notes: list[str] = []

    if not plan.generated_tasks:
        notes.append("Plan has no generated tasks.")

    if plan.estimated_duration is None or plan.estimated_duration <= 0:
        notes.append("Plan is missing a positive estimated duration.")

    blank_titles = sum(1 for task in plan.generated_tasks if not task.title.strip())
    if blank_titles:
        notes.append(f"Plan has {blank_titles} task(s) with a blank title.")

    return ReviewResult(passed=not notes, notes=notes)
