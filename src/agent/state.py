"""Shared state passed between nodes in the academic-agent LangGraph workflow."""

from typing import TypedDict

from ..models.project import Project
from ..planner.planner_result import PlannerResult
from ..tools.paper_result import PaperResult


class AgentState(TypedDict, total=False):
    """State threaded through build_search_query -> search_papers -> generate_plan
    -> review_plan, with review_plan conditionally looping back to generate_plan.

    Each node reads the keys it needs off this dict and returns only the keys
    it adds or changes; LangGraph merges that partial dict back into the
    shared state before running the next node. ``total=False`` reflects that
    keys are filled in gradually as the graph runs, not all present upfront.
    """

    project: Project
    search_query: str
    papers: list[PaperResult]
    warnings: list[str]
    plan: PlannerResult

    # Populated by review_plan; read by the conditional edge's router.
    review_passed: bool
    review_notes: list[str]
    retry_count: int
