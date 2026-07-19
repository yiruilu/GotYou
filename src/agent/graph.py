"""Assembles the nodes into the academic-agent LangGraph workflow.

    START -> build_search_query -> search_papers -> generate_plan -> review_plan
                                                          ^                |
                                                          |                v
                                                          +---- (failed, retry) --- (passed / retries exhausted) -> END

review_plan is the graph's one conditional edge: route_after_review inspects
review_passed/retry_count in the shared state and sends execution either back
to generate_plan (one retry only) or on to END.
"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from ..services.planning_service import PlanningService
from ..tools.paper_search_tool import PaperSearchTool
from .nodes import (
    build_search_query,
    make_generate_plan_node,
    make_search_papers_node,
    review_plan,
    route_after_review,
)
from .state import AgentState


def build_agent_graph(
    paper_search_tool: PaperSearchTool, planning_service: PlanningService
) -> CompiledStateGraph:
    """Wire the nodes into a graph, with a conditional edge after generate_plan, and compile it."""
    graph = StateGraph(AgentState)

    graph.add_node("build_search_query", build_search_query)
    graph.add_node("search_papers", make_search_papers_node(paper_search_tool))
    graph.add_node("generate_plan", make_generate_plan_node(planning_service))
    graph.add_node("review_plan", review_plan)

    graph.add_edge(START, "build_search_query")
    graph.add_edge("build_search_query", "search_papers")
    graph.add_edge("search_papers", "generate_plan")
    graph.add_edge("generate_plan", "review_plan")
    graph.add_conditional_edges("review_plan", route_after_review, {"generate_plan": "generate_plan", END: END})

    return graph.compile()
