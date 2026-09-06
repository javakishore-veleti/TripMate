from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from overrides import override

from middleware.adapters.agentic.interfaces import AgenticFrameworkAdapter
from middleware.adapters.agentic.langgraph.dashboard.places_planner.main import resolve_brief_jobs
from middleware.adapters.agentic.langgraph.llm_text import empty_constraints
from middleware.adapters.agentic.langgraph.pipeline_flavor import flavor_lines, with_flavor
from middleware.adapters.agentic.langgraph.runtime import (
    DEFAULT_MAX_STEPS,
    graph_config,
    halt_node,
    with_runtime,
)
from middleware.adapters.agentic.langgraph.routes import (
    ROUTE_MAP,
    route_after_draft,
    route_after_intake,
    route_after_specialist,
    route_from_coordinator,
)
from middleware.adapters.agentic.langgraph.specialists import (
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
from middleware.adapters.agentic.langgraph.specialists.ids import (
    AIR_RESEARCH,
    CLIMATE_BRIEF,
    COORDINATOR,
    COST_REVIEW,
    HALT,
    INTAKE,
    PLAN_ASSEMBLE,
    REQUEST_DECLINED,
    STAY_RESEARCH,
    TRAVELER_REVIEW,
    TRIP_DRAFT,
)
from middleware.adapters.agentic.langgraph.utils import _serialize_result
from middleware.persistence.checkpointer import build_checkpointer
from middleware.common.app_constants import ResponseCode
from middleware.common.dtos import TravelReqCtx, TravelRequest, TravelState
from middleware.common.log import get_logger
from middleware.modules.shared.services.pipeline_cancel_service import (
    PipelineCancelled,
    raise_if_cancelled,
)
from middleware.modules.shared.services.service_names import SERVICE_RUN_TRACE

logger = get_logger(__name__)

_STEP = {
    INTAKE: "Reading your trip ask.",
    COORDINATOR: "Choosing what to research.",
    AIR_RESEARCH: "Looking at flights.",
    STAY_RESEARCH: "Looking at stays.",
    CLIMATE_BRIEF: "Checking the weather.",
    COST_REVIEW: "Checking the budget.",
    TRIP_DRAFT: "Writing the draft.",
    TRAVELER_REVIEW: "Pausing for your review.",
    PLAN_ASSEMBLE: "Putting the days together.",
    REQUEST_DECLINED: "Could not take this ask.",
    HALT: "This plan stopped after too many steps.",
}


def _public_step(node: str) -> str | None:
    if node == "__interrupt__":
        return TRAVELER_REVIEW
    if node.startswith("__"):
        return None
    return node if node in _STEP else None


def _pipeline_line(ctx: TravelReqCtx, line: str) -> None:
    if not ctx.user_id or not ctx.thread_id:
        return
    from middleware.modules.shared.services.objects import ServicesObjectFactory

    ServicesObjectFactory.get_service(SERVICE_RUN_TRACE).write(ctx.user_id, ctx.thread_id, line)


def _step_line(label: str, flavors: dict[str, str], key: str) -> str:
    return with_flavor(label, flavors.get(key, ""))


class TripComposeAdapter(AgenticFrameworkAdapter[TravelRequest, TravelReqCtx]):
    def __init__(self):
        graph = StateGraph(TravelState)
        graph.add_node(INTAKE, with_runtime(INTAKE, intake))
        graph.add_node(COORDINATOR, with_runtime(COORDINATOR, coordinator))
        graph.add_node(REQUEST_DECLINED, with_runtime(REQUEST_DECLINED, request_declined))
        graph.add_node(AIR_RESEARCH, with_runtime(AIR_RESEARCH, air_research))
        graph.add_node(STAY_RESEARCH, with_runtime(STAY_RESEARCH, stay_research))
        graph.add_node(CLIMATE_BRIEF, with_runtime(CLIMATE_BRIEF, climate_brief))
        graph.add_node(COST_REVIEW, with_runtime(COST_REVIEW, cost_review))
        graph.add_node(TRIP_DRAFT, with_runtime(TRIP_DRAFT, trip_draft))
        graph.add_node(TRAVELER_REVIEW, with_runtime(TRAVELER_REVIEW, traveler_review))
        graph.add_node(PLAN_ASSEMBLE, with_runtime(PLAN_ASSEMBLE, plan_assemble))
        graph.add_node(HALT, with_runtime(HALT, halt_node))

        graph.add_edge(START, INTAKE)
        graph.add_conditional_edges(INTAKE, route_after_intake, ROUTE_MAP)
        graph.add_conditional_edges(COORDINATOR, route_from_coordinator, ROUTE_MAP)
        graph.add_conditional_edges(AIR_RESEARCH, route_after_specialist(AIR_RESEARCH), ROUTE_MAP)
        graph.add_conditional_edges(STAY_RESEARCH, route_after_specialist(STAY_RESEARCH), ROUTE_MAP)
        graph.add_conditional_edges(CLIMATE_BRIEF, route_after_specialist(CLIMATE_BRIEF), ROUTE_MAP)
        graph.add_conditional_edges(COST_REVIEW, route_after_specialist(COST_REVIEW), ROUTE_MAP)
        graph.add_conditional_edges(TRIP_DRAFT, route_after_draft, ROUTE_MAP)
        graph.add_edge(TRAVELER_REVIEW, PLAN_ASSEMBLE)
        graph.add_edge(PLAN_ASSEMBLE, END)
        graph.add_edge(REQUEST_DECLINED, END)
        graph.add_edge(HALT, END)
        self._graph = graph.compile(checkpointer=build_checkpointer())

    @override
    def execute(self, request: TravelRequest, ctx: TravelReqCtx) -> int:
        user_input = (ctx.user_message or request.message).strip()
        config = graph_config(ctx)
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

        payload = (
            Command(
                resume={
                    "approved": ctx.approved,
                    "feedback": ctx.feedback,
                }
            )
            if resuming
            else {
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
                "current_step": INTAKE,
                "step_count": 0,
                "max_steps": DEFAULT_MAX_STEPS,
                "error_count": 0,
                "last_error": None,
                "proposed_action": {},
                "llm_provider": ctx.llm_provider,
                "llm_model": ctx.llm_model,
                "llm_base_url": ctx.llm_base_url,
                "llm_jobs": jobs,
                "user_id": ctx.user_id,
                "user_preferences": ctx.user_preferences or {},
            }
        )
        result = {}
        flavors: dict[str, str] = {}
        saw_review = False
        try:
            raise_if_cancelled()
            flavors = flavor_lines(
                user_input,
                {
                    "user_id": ctx.user_id,
                    "user_preferences": ctx.user_preferences or {},
                    "llm_provider": ctx.llm_provider,
                    "llm_model": ctx.llm_model,
                    "llm_base_url": ctx.llm_base_url,
                    "llm_jobs": jobs,
                },
            )
            if resuming:
                _pipeline_line(
                    ctx,
                    _step_line("You approved. Polishing the final plan.", flavors, PLAN_ASSEMBLE),
                )
            else:
                _pipeline_line(ctx, _step_line("Started your trip sketch.", flavors, "started"))
                _pipeline_line(ctx, _step_line("Opening the planner.", flavors, "opening"))
                _pipeline_line(ctx, _step_line("Reading your trip ask.", flavors, INTAKE))
            for chunk in self._graph.stream(payload, config=config, stream_mode="updates"):
                raise_if_cancelled()
                for node, update in chunk.items():
                    logger.info("trip compose node=%s thread=%s", node, ctx.thread_id)
                    step = _public_step(str(node))
                    if step == TRAVELER_REVIEW:
                        if not saw_review:
                            _pipeline_line(
                                ctx,
                                _step_line(_STEP[TRAVELER_REVIEW], flavors, TRAVELER_REVIEW),
                            )
                            saw_review = True
                    elif step and step != INTAKE:
                        _pipeline_line(ctx, _step_line(_STEP[step], flavors, step))
                    if isinstance(update, dict):
                        result.update(update)
                raise_if_cancelled()
        except PipelineCancelled:
            _pipeline_line(ctx, "Stopped. You cancelled this draft.")
            result = dict(result)
            result["cancelled"] = True
            result["request_accepted"] = False
            result["request_note"] = "You stopped this draft."
            ctx.api_response.result = _serialize_result(result, ctx.thread_id, next_nodes=())
            ctx.api_response.message = "Draft cancelled."
            return ResponseCode.SUCCESS

        snapshot = self._graph.get_state(config)
        if snapshot.values:
            result = snapshot.values
        ctx.api_response.result = _serialize_result(
            result,
            ctx.thread_id,
            next_nodes=snapshot.next,
        )
        if ctx.api_response.result.get("requires_approval"):
            if not saw_review:
                _pipeline_line(
                    ctx,
                    _step_line(_STEP[TRAVELER_REVIEW], flavors, TRAVELER_REVIEW),
                )
        else:
            _pipeline_line(ctx, _step_line("Finished this pass.", flavors, "finished"))
        logger.info(
            "trip compose %s done thread=%s requires_approval=%s specialists=%s llm_calls=%s",
            mode,
            ctx.thread_id,
            ctx.api_response.result.get("requires_approval"),
            ctx.api_response.result.get("selected_specialists"),
            ctx.api_response.result.get("llm_calls"),
        )
        return ResponseCode.SUCCESS
