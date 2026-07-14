"""LLMPlanner: generates a task list by asking an LLM for structured JSON output."""

import json
import os
from datetime import date

import anthropic

from ..models.enums import Priority, TaskStatus
from ..models.project import Project
from ..models.task import Task
from .planner import Planner
from .planner_result import PlannerResult

DEFAULT_MODEL = "claude-opus-4-8"
DEFAULT_MAX_TOKENS = 4096

_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "tasks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": [p.value for p in Priority]},
                    "status": {"type": "string", "enum": [s.value for s in TaskStatus]},
                    "estimated_time": {"type": ["number", "null"]},
                    "due_date": {"type": ["string", "null"]},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "id",
                    "title",
                    "description",
                    "priority",
                    "status",
                    "estimated_time",
                    "due_date",
                    "dependencies",
                ],
                "additionalProperties": False,
            },
        },
        "estimated_duration": {"type": ["number", "null"]},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["tasks", "estimated_duration", "warnings"],
    "additionalProperties": False,
}


class LLMProviderError(RuntimeError):
    """Raised when the LLM provider fails to return a usable response."""


class AnthropicProvider:
    """Thin wrapper around the Anthropic SDK.

    Isolated so a different provider (OpenAI, a local model, ...) can be
    swapped in later without touching LLMPlanner's prompt or parsing logic.
    """

    def __init__(self, model: str = DEFAULT_MODEL, max_tokens: int = DEFAULT_MAX_TOKENS):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise LLMProviderError(
                "ANTHROPIC_API_KEY is not set. Add it to your environment or a .env file."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    def generate_json(self, prompt: str) -> dict:
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                output_config={"format": {"type": "json_schema", "schema": _PLAN_SCHEMA}},
                messages=[{"role": "user", "content": prompt}],
            )
        except anthropic.APIError as exc:
            raise LLMProviderError(f"LLM request failed: {exc}") from exc

        text = next((block.text for block in response.content if block.type == "text"), None)
        if text is None:
            raise LLMProviderError("LLM response contained no text content.")

        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMProviderError(f"LLM response was not valid JSON: {exc}") from exc


class LLMPlanner(Planner):
    """Asks an LLM to turn a project's goal, deadline, feedback, resources, and
    existing tasks into a structured task plan."""

    def __init__(self, provider: AnthropicProvider | None = None):
        self._provider = provider

    def plan(self, project: Project) -> PlannerResult:
        warnings: list[str] = []

        try:
            provider = self._provider or AnthropicProvider()
        except LLMProviderError as exc:
            warnings.append(str(exc))
            return PlannerResult(planner_name="LLMPlanner", warnings=warnings)

        try:
            data = provider.generate_json(self._build_prompt(project))
        except LLMProviderError as exc:
            warnings.append(str(exc))
            return PlannerResult(planner_name="LLMPlanner", warnings=warnings)

        tasks, parse_warnings = self._parse_tasks(data.get("tasks", []))
        warnings.extend(parse_warnings)
        warnings.extend(data.get("warnings", []))

        return PlannerResult(
            planner_name="LLMPlanner",
            generated_tasks=tasks,
            estimated_duration=data.get("estimated_duration"),
            warnings=warnings,
        )

    def _build_prompt(self, project: Project) -> str:
        feedback_lines = "\n".join(f"- ({f.source}) {f.content}" for f in project.feedback) or "None"
        resource_lines = "\n".join(f"- {r.title} ({r.type.value})" for r in project.resources) or "None"
        task_lines = "\n".join(f"- {t.title} [{t.status.value}]" for t in project.tasks) or "None"
        deadline = project.deadline.isoformat() if project.deadline else "None"

        return f"""You are an academic coach. Create a task plan for this project.

Goal: {project.goal}
Deadline: {deadline}

Existing feedback:
{feedback_lines}

Existing resources:
{resource_lines}

Existing tasks:
{task_lines}

Generate a list of concrete, actionable tasks that move this project toward its
goal, taking the deadline and feedback into account. Each task needs a unique id,
a title, a short description, a priority (low/medium/high), a status (use "todo"
for all new tasks), an estimated_time in hours (or null), a due_date in
YYYY-MM-DD format that does not exceed the project deadline (or null), and a list
of dependency task ids (can be empty). If the goal is too vague to plan from,
return an empty tasks list and explain why in warnings."""

    def _parse_tasks(self, raw_tasks: list[dict]) -> tuple[list[Task], list[str]]:
        tasks: list[Task] = []
        warnings: list[str] = []
        required_fields = {"id", "title", "priority", "status"}

        for index, raw in enumerate(raw_tasks):
            missing = required_fields - raw.keys()
            if missing:
                warnings.append(f"Task at index {index} is missing fields {sorted(missing)}; skipped.")
                continue

            try:
                priority = Priority(raw["priority"])
                status = TaskStatus(raw["status"])
            except ValueError as exc:
                warnings.append(f"Task '{raw.get('title', index)}' has an invalid field value: {exc}; skipped.")
                continue

            due_date = None
            if raw.get("due_date"):
                try:
                    due_date = date.fromisoformat(raw["due_date"])
                except ValueError:
                    warnings.append(f"Task '{raw['title']}' has an invalid due_date; ignored.")

            tasks.append(
                Task(
                    id=raw["id"],
                    title=raw["title"],
                    description=raw.get("description", ""),
                    priority=priority,
                    status=status,
                    estimated_time=raw.get("estimated_time"),
                    due_date=due_date,
                    dependencies=raw.get("dependencies", []),
                )
            )

        return tasks, warnings
