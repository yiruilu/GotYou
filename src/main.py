"""Entry point: run sample projects through LLMPlanner and PlanningService."""

from datetime import date, timedelta

from .models import Feedback, Priority, Project, Resource, ResourceType
from .planner import LLMPlanner, PlannerResult
from .services import PlanningService


def _print_result(title: str, project: Project, result: PlannerResult) -> None:
    print(f"\n=== {title} ===")
    print(f"Goal: {project.goal}")
    print(f"Planner: {result.planner_name}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

    if not result.generated_tasks:
        print("No tasks generated.")
        return

    print(f"Estimated duration: {result.estimated_duration} hours")
    print("Generated tasks:")
    for task in result.generated_tasks:
        due = task.due_date.isoformat() if task.due_date else "no due date"
        print(f"  [{task.priority.value:6}] {task.title} (due {due})")
        if task.description:
            print(f"           {task.description}")


def run_paper_revision_example() -> None:
    project = Project(
        id="proj-1",
        title="Revise NeurIPS Submission",
        goal="Revise my machine learning research paper for resubmission after peer review",
        deadline=date.today() + timedelta(days=7),
        resources=[
            Resource(
                id="res-1",
                title="Attention Is All You Need",
                type=ResourceType.PAPER,
                source="arxiv.org/abs/1706.03762",
                summary="Foundational transformer architecture paper.",
                relevance="Directly relevant to strengthening the related work section.",
            ),
        ],
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

    service = PlanningService(LLMPlanner())
    result = service.generate_plan(project)
    _print_result("Paper Revision (LLMPlanner)", project, result)


def run_manual_evaluations() -> None:
    service = PlanningService(LLMPlanner())

    detailed_paper = Project(
        id="eval-1",
        title="Journal Resubmission",
        goal=(
            "Revise my paper's methodology and experiments section to address "
            "reviewer concerns about insufficient baseline comparisons, then "
            "resubmit to the journal."
        ),
        deadline=date.today() + timedelta(days=10),
        feedback=[
            Feedback(
                id="fb-2",
                source="reviewer_1",
                content="Missing comparison against two standard baselines.",
                category="experiments",
                priority=Priority.HIGH,
            ),
        ],
    )
    _print_result(
        "Eval 1: Detailed paper revision request",
        detailed_paper,
        service.generate_plan(detailed_paper),
    )

    vague_request = Project(
        id="eval-2",
        title="Untitled Project",
        goal="Help me get better at my research",
    )
    _print_result(
        "Eval 2: Vague request, missing information",
        vague_request,
        service.generate_plan(vague_request),
    )

    leetcode_request = Project(
        id="eval-3",
        title="Interview Prep",
        goal="Practice Leetcode problems daily to prepare for software engineering interviews",
        deadline=date.today() + timedelta(days=30),
    )
    _print_result(
        "Eval 3: Leetcode request (outside the research MVP)",
        leetcode_request,
        service.generate_plan(leetcode_request),
    )


if __name__ == "__main__":
    run_paper_revision_example()
    run_manual_evaluations()
