from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from overrides import override

from adapters.persistence.checkpointer import build_checkpointer

from adapters.agentic.interfaces import AgenticFrameworkAdapter
from adapters.agentic.langgraph.agents import (
    budget_agent,
    final_agent,
    flight_agent,
    guardrail_blocked_agent,
    hotel_agent,
    human_approval_agent,
    itinerary_agent,
    supervisor_agent,
    weather_agent,
)
from adapters.agentic.langgraph.agents.utils import empty_constraints
from adapters.agentic.langgraph.routes import (
    ROUTE_MAP,
    route_after_agent,
    route_from_supervisor,
)
from adapters.agentic.langgraph.utils import _serialize_result
from common.app_constants import ResponseCode
from common.dtos import TravelReqCtx, TravelRequest, TravelState
from common.log import get_logger

logger = get_logger(__name__)


class TravelPlannerLangGraphAdapter(AgenticFrameworkAdapter[TravelRequest, TravelReqCtx]):
    def __init__(self):
        # =========================
        # Build Graph
        # =========================
        graph = StateGraph(TravelState)

        graph.add_node("supervisor", supervisor_agent)
        graph.add_node("guardrail_blocked", guardrail_blocked_agent)
        graph.add_node("flight_agent", flight_agent)
        graph.add_node("hotel_agent", hotel_agent)
        graph.add_node("weather_agent", weather_agent)
        graph.add_node("budget_agent", budget_agent)
        graph.add_node("itinerary_agent", itinerary_agent)
        graph.add_node("human_approval", human_approval_agent)
        graph.add_node("final_agent", final_agent)

        graph.add_edge(START, "supervisor")
        graph.add_conditional_edges("supervisor", route_from_supervisor, ROUTE_MAP)

        graph.add_conditional_edges(
            "flight_agent", route_after_agent("flight_agent"), ROUTE_MAP
        )
        graph.add_conditional_edges(
            "hotel_agent", route_after_agent("hotel_agent"), ROUTE_MAP
        )
        graph.add_conditional_edges(
            "weather_agent", route_after_agent("weather_agent"), ROUTE_MAP
        )
        graph.add_conditional_edges(
            "budget_agent", route_after_agent("budget_agent"), ROUTE_MAP
        )

        graph.add_edge("itinerary_agent", "human_approval")
        graph.add_edge("human_approval", "final_agent")
        graph.add_edge("final_agent", END)
        graph.add_edge("guardrail_blocked", END)
        self._travel_planner_graph = graph.compile(checkpointer=build_checkpointer())

    @override
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        user_input = (ctx.user_message or request.message).strip()
        config = {"configurable": {"thread_id": ctx.thread_id}}
        resuming = ctx.approved or bool(ctx.feedback.strip())
        mode = "resume" if resuming else "draft"
        logger.info(
            "graph %s thread=%s provider=%s model=%s",
            mode,
            ctx.thread_id,
            ctx.llm_provider,
            ctx.llm_model,
        )

        if resuming:
            result = self._travel_planner_graph.invoke(
                Command(
                    resume={
                        "approved": ctx.approved,
                        "feedback": ctx.feedback,
                    }
                ),
                config=config,
            )
        else:
            result = self._travel_planner_graph.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "user_query": user_input,
                    "guardrail_allowed": True,
                    "guardrail_reason": "",
                    "selected_agents": [],
                    "trip_constraints": empty_constraints(),
                    "supervisor_reasoning": "",
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "budget_results": "",
                    "itinerary": "",
                    "approval_request": "",
                    "approved": False,
                    "human_feedback": "",
                    "final_response": "",
                    "llm_calls": 0,
                    "llm_provider": ctx.llm_provider,
                    "llm_model": ctx.llm_model,
                    "llm_base_url": ctx.llm_base_url,
                    "user_id": ctx.user_id,
                    "user_preferences": ctx.user_preferences or {},
                },
                config=config,
            )

        snapshot = self._travel_planner_graph.get_state(config)
        ctx.api_response.result = _serialize_result(
            result,
            ctx.thread_id,
            next_nodes=snapshot.next,
        )
        logger.info(
            "graph %s done thread=%s requires_approval=%s agents=%s llm_calls=%s",
            mode,
            ctx.thread_id,
            ctx.api_response.result.get("requires_approval"),
            ctx.api_response.result.get("selected_agents"),
            ctx.api_response.result.get("llm_calls"),
        )
        return ResponseCode.SUCCESS
