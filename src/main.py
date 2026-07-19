"""Entry point: run the GotYou research agent as a LangGraph workflow.

Pipeline (LangGraph StateGraph): user research goal -> build_search_query
-> search_papers (PaperSearchTool/arXiv) -> generate_plan (LLMPlanner/OpenAI)
-> structured plan -> terminal output.
"""

from datetime import date, timedelta

from .agent import AgentState, build_agent_graph
from .models import Feedback, Priority, Project
from .planner import LLMPlanner
from .services import PlanningService
from .tools import PaperSearchTool


def _print_result(state: AgentState) -> None:
    project = state["project"]
    plan = state["plan"]

    print(f"=== {project.title} ===")
    print(f"Research goal: {project.goal}")
    print(f"Search query: {state['search_query']}")

    print(f"\nPapers found ({len(state['papers'])}):")
    if not state["papers"]:
        print("  (none)")
    for paper in state["papers"]:
        print(f"  - {paper.title} ({paper.year or 'n.d.'}) - {paper.url}")

    print(f"\nGenerated tasks ({len(plan.generated_tasks)}):")
    if not plan.generated_tasks:
        print("  (none)")
    for task in plan.generated_tasks:
        due = task.due_date.isoformat() if task.due_date else "no due date"
        print(f"  [{task.priority.value:6}] {task.title} (due {due})")
        if task.description:
            print(f"           {task.description}")

    duration = f"{plan.estimated_duration} hours" if plan.estimated_duration else "n/a"
    print(f"\nEstimated duration: {duration}")

    if plan.warnings:
        print("\nWarnings:")
        for warning in plan.warnings:
            print(f"  - {warning}")

    verdict = "PASSED" if state.get("review_passed") else "FAILED"
    print(f"\nPlan review: {verdict} (retries used: {state.get('retry_count', 0)})")
    for note in state.get("review_notes", []):
        print(f"  - {note}")


def main() -> None:
    project = Project(
        id="proj-1",
        title="Revise NeurIPS Submission",
        goal="Revise my machine learning research paper for resubmission after peer review",
        deadline=date.today() + timedelta(days=7),
        feedback=[
            Feedback(
                id="fb-1",
                source="reviewer_2",
                content=(
                    "The related work section is weak — it fails to position this paper "
                    "against recent transformer-based approaches and omits several "
                    "directly competing methods published in the last two years."
                ),
                category="related_work",
                priority=Priority.HIGH,
            ),
        ],
    )

    graph = build_agent_graph(
        paper_search_tool=PaperSearchTool(),
        planning_service=PlanningService(LLMPlanner()),
    )
    final_state = graph.invoke(AgentState(project=project, warnings=[]))
    _print_result(final_state)


if __name__ == "__main__":
    main()
