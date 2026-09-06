from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from overrides import override

from middleware.adapters.agentic.interfaces import AgenticFrameworkAdapter
from middleware.modules.travel_search.workflows.places_planner.main import resolve_brief_jobs
from middleware.adapters.agentic.langgraph.llm_text import empty_constraints
from middleware.adapters.agentic.langgraph.routes import (
    ROUTE_MAP,
    route_after_intake,
    route_after_specialist,
    route_from_coordinator,
)
from middleware.modules.plans_mgmt.tasks.specialists import (
    air_research,
    climate_brief,
    coordinator,
    cost_review,
    intake,
    plan_assemble,
    request_declined,
    stay_research,
    traveler_review,
    trip_draft,
)
from middleware.modules.plans_mgmt.tasks.specialists.ids import (
    AIR_RESEARCH,
    CLIMATE_BRIEF,
    COORDINATOR,
    COST_REVIEW,
    INTAKE,
    PLAN_ASSEMBLE,
    REQUEST_DECLINED,
    STAY_RESEARCH,
    TRAVELER_REVIEW,
    TRIP_DRAFT,
)
from middleware.adapters.agentic.langgraph.utils import _serialize_result
from middleware.adapters.persistence.checkpointer import build_checkpointer
from middleware.common.app_constants import ResponseCode
from middleware.common.dtos import TravelReqCtx, TravelRequest, TravelState
from middleware.common.log import get_logger

logger = get_logger(__name__)


class TripComposeAdapter(AgenticFrameworkAdapter[TravelRequest, TravelReqCtx]):
    def __init__(self):
        graph = StateGraph(TravelState)
        graph.add_node(INTAKE, intake)
        graph.add_node(COORDINATOR, coordinator)
        graph.add_node(REQUEST_DECLINED, request_declined)
        graph.add_node(AIR_RESEARCH, air_research)
        graph.add_node(STAY_RESEARCH, stay_research)
        graph.add_node(CLIMATE_BRIEF, climate_brief)
        graph.add_node(COST_REVIEW, cost_review)
        graph.add_node(TRIP_DRAFT, trip_draft)
        graph.add_node(TRAVELER_REVIEW, traveler_review)
        graph.add_node(PLAN_ASSEMBLE, plan_assemble)

        graph.add_edge(START, INTAKE)
        graph.add_conditional_edges(INTAKE, route_after_intake, ROUTE_MAP)
        graph.add_conditional_edges(COORDINATOR, route_from_coordinator, ROUTE_MAP)
        graph.add_conditional_edges(AIR_RESEARCH, route_after_specialist(AIR_RESEARCH), ROUTE_MAP)
        graph.add_conditional_edges(STAY_RESEARCH, route_after_specialist(STAY_RESEARCH), ROUTE_MAP)
        graph.add_conditional_edges(CLIMATE_BRIEF, route_after_specialist(CLIMATE_BRIEF), ROUTE_MAP)
        graph.add_conditional_edges(COST_REVIEW, route_after_specialist(COST_REVIEW), ROUTE_MAP)
        graph.add_edge(TRIP_DRAFT, TRAVELER_REVIEW)
        graph.add_edge(TRAVELER_REVIEW, PLAN_ASSEMBLE)
        graph.add_edge(PLAN_ASSEMBLE, END)
        graph.add_edge(REQUEST_DECLINED, END)
        self._graph = graph.compile(checkpointer=build_checkpointer())

    @override
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        user_input = (ctx.user_message or request.message).strip()
        config = {"configurable": {"thread_id": ctx.thread_id}}
        jobs = resolve_brief_jobs(
            ctx.user_preferences or {},
            default_provider=ctx.llm_provider,
            default_model=ctx.llm_model,
            default_url=ctx.llm_base_url,
        )
        resuming = ctx.approved or bool(ctx.feedback.strip())
        mode = "resume" if resuming else "draft"
        logger.info(
            "trip compose %s thread=%s provider=%s model=%s",
            mode,
            ctx.thread_id,
            ctx.llm_provider,
            ctx.llm_model,
        )

        if resuming:
            result = self._graph.invoke(
                Command(
                    resume={
                        "approved": ctx.approved,
                        "feedback": ctx.feedback,
                    }
                ),
                config=config,
            )
        else:
            result = self._graph.invoke(
                {
                    "messages": [HumanMessage(content=user_input)],
                    "user_query": user_input,
                    "request_accepted": True,
                    "request_note": "",
                    "selected_specialists": [],
                    "trip_constraints": empty_constraints(),
                    "coordinator_notes": "",
                    "flight_results": "",
                    "hotel_results": "",
                    "weather_results": "",
                    "budget_results": "",
                    "itinerary": "",
                    "approval_request": "",
                    "approved": False,
                    "traveler_feedback": "",
                    "final_response": "",
                    "llm_calls": 0,
                    "llm_provider": ctx.llm_provider,
                    "llm_model": ctx.llm_model,
                    "llm_base_url": ctx.llm_base_url,
                    "llm_jobs": jobs,
                    "user_id": ctx.user_id,
                    "user_preferences": ctx.user_preferences or {},
                },
                config=config,
            )

        snapshot = self._graph.get_state(config)
        ctx.api_response.result = _serialize_result(
            result,
            ctx.thread_id,
            next_nodes=snapshot.next,
        )
        logger.info(
            "trip compose %s done thread=%s requires_approval=%s specialists=%s llm_calls=%s",
            mode,
            ctx.thread_id,
            ctx.api_response.result.get("requires_approval"),
            ctx.api_response.result.get("selected_specialists"),
            ctx.api_response.result.get("llm_calls"),
        )
        return ResponseCode.SUCCESS
