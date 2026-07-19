"""Node functions for the academic-agent LangGraph workflow.

Each node is a plain function of (state) -> partial state update, which is
LangGraph's node contract. ``build_search_query`` needs nothing but the
state, so it's a bare function. ``search_papers`` and ``generate_plan``
depend on a tool/service instance that isn't part of AgentState, so they're
built by factory functions that close over the dependency and return the
actual node callable.
"""

import re
from collections.abc import Callable

from langgraph.graph import END

from ..models.enums import Priority
from ..services.planning_service import PlanningService
from ..tools.paper_search_tool import PaperSearchError, PaperSearchTool
from .reviewer import review_plan_rules
from .state import AgentState

_MAX_QUERY_KEYWORDS = 3
_PRIORITY_RANK = {Priority.HIGH: 2, Priority.MEDIUM: 1, Priority.LOW: 0}

# One retry: if the plan still fails review after being regenerated once,
# stop and return whatever we have rather than looping forever.
MAX_REVIEW_RETRIES = 1

# Generic English stopwords plus generic academic-writing nouns/verbs
# ("paper", "section", "weak", "fails", ...) that are common in goals and
# reviewer feedback but useless as search terms.
_STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "so", "as", "at", "by",
    "for", "from", "in", "into", "of", "on", "onto", "to", "with", "without", "within",
    "about", "against", "after", "before", "during", "between", "through", "over",
    "under", "up", "down", "out", "off", "again", "further", "once", "here", "there",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most",
    "other", "some", "such", "no", "nor", "not", "only", "own", "same", "too", "very",
    "can", "will", "just", "should", "now", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "having", "do", "does", "did", "doing", "it", "its",
    "this", "that", "these", "those", "i", "me", "my", "we", "our", "you", "your", "he",
    "she", "they", "them", "their", "several", "directly", "recent", "based",
    "published", "last", "two", "one", "help", "get", "better", "paper", "papers",
    "section", "sections", "work", "related", "approach", "approaches", "method",
    "methods", "result", "results", "review", "reviews", "study", "studies",
    "research", "researcher", "resubmission", "revise", "revision", "weak", "fails",
    "fail", "omits", "omit", "missing", "lacks", "lack", "insufficient", "unclear",
    "poor", "poorly", "position", "peer",
})


def build_search_query(state: AgentState) -> dict:
    """Node 1: derive arXiv search keywords from the goal, then reviewer feedback."""
    project = state["project"]

    top_feedback = None
    if project.feedback:
        top_feedback = max(project.feedback, key=lambda f: _PRIORITY_RANK.get(f.priority, 0))

    texts = [project.goal]
    if top_feedback:
        texts.append(top_feedback.content)

    keywords: list[str] = []
    for text in texts:
        for word in re.findall(r"[a-zA-Z]+", text.lower()):
            if len(word) < 3 or word in _STOPWORDS or word in keywords:
                continue
            keywords.append(word)
            if len(keywords) >= _MAX_QUERY_KEYWORDS:
                return {"search_query": " ".join(keywords)}

    query = " ".join(keywords) if keywords else project.goal
    return {"search_query": query}


def make_search_papers_node(paper_search_tool: PaperSearchTool) -> Callable[[AgentState], dict]:
    """Node 2 factory: bind a PaperSearchTool instance and return the search_papers node."""

    def search_papers(state: AgentState) -> dict:
        query = state["search_query"]
        warnings: list[str] = []

        try:
            papers = paper_search_tool.run(query=query)
        except PaperSearchError as exc:
            papers = []
            warnings.append(str(exc))
        else:
            if not papers:
                warnings.append(f"No papers found for search query '{query}'.")

        return {"papers": papers, "warnings": [*state.get("warnings", []), *warnings]}

    return search_papers


def make_generate_plan_node(planning_service: PlanningService) -> Callable[[AgentState], dict]:
    """Node 3 factory: bind a PlanningService instance and return the generate_plan node."""

    def generate_plan(state: AgentState) -> dict:
        plan = planning_service.generate_plan(state["project"], papers=state.get("papers", []))
        plan.warnings = [*state.get("warnings", []), *plan.warnings]
        return {"plan": plan}

    return generate_plan


def review_plan(state: AgentState) -> dict:
    """Node 4: run the rule-based reviewer against the latest plan.

    On failure, bumps retry_count so the router (route_after_review) knows
    whether a retry has already been spent.
    """
    result = review_plan_rules(state["plan"])
    retry_count = state.get("retry_count", 0)
    if not result.passed:
        retry_count += 1

    return {
        "review_passed": result.passed,
        "review_notes": result.notes,
        "retry_count": retry_count,
    }


def route_after_review(state: AgentState) -> str:
    """Conditional edge router: decide the next node after review_plan.

    - Review passed -> END.
    - Review failed and the one allowed retry hasn't been used yet ->
      loop back to generate_plan.
    - Review failed again after that retry -> END anyway, so a plan that
      keeps failing review can't loop forever.
    """
    if state.get("review_passed"):
        return END
    if state.get("retry_count", 0) <= MAX_REVIEW_RETRIES:
        return "generate_plan"
    return END
