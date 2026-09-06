import operator
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import AnyMessage

from pydantic import BaseModel, Field, field_validator

from common.constants.agentic_adapters import AGENTIC_ADAPTER_LANGGRAPH
from common.llm_catalog import DEFAULT_LLM_MODEL, DEFAULT_LLM_PROVIDER


def _or_default(value: str | None, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None
    agentic_adapter: str = AGENTIC_ADAPTER_LANGGRAPH
    llm_provider: str = DEFAULT_LLM_PROVIDER
    llm_model: str = DEFAULT_LLM_MODEL
    llm_base_url: str = ""

    @field_validator("agentic_adapter", mode="before")
    @classmethod
    def default_agentic_adapter(cls, value: str | None) -> str:
        return _or_default(value, AGENTIC_ADAPTER_LANGGRAPH)

    @field_validator("llm_provider", mode="before")
    @classmethod
    def default_llm_provider(cls, value: str | None) -> str:
        return _or_default(value, DEFAULT_LLM_PROVIDER)

    @field_validator("llm_model", mode="before")
    @classmethod
    def default_llm_model(cls, value: str | None) -> str:
        return _or_default(value, DEFAULT_LLM_MODEL)


class TravelAPIResponse(BaseModel):
    status_code: int = 200
    message: str = "Success"
    result: dict = {}


class TravelResponse(BaseModel):
    success: bool = True
    thread_id: str | None = None
    status_code: int = 200
    message: str = "Success"
    result: dict = {}


class TravelReqCtx(BaseModel):
    thread_id: str = Field(min_length=1)
    approved: bool
    feedback: str = ""
    user_message: str = ""
    user_id: str = ""
    user_preferences: dict = Field(default_factory=dict)
    agentic_adapter: str = AGENTIC_ADAPTER_LANGGRAPH
    llm_provider: str = DEFAULT_LLM_PROVIDER
    llm_model: str = DEFAULT_LLM_MODEL
    llm_base_url: str = ""
    api_response: TravelAPIResponse = TravelAPIResponse(
        status_code=200, message="Success", result={}
    )


class ApprovalRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    approved: bool
    feedback: str = ""
    agentic_adapter: str = AGENTIC_ADAPTER_LANGGRAPH
    llm_provider: str = DEFAULT_LLM_PROVIDER
    llm_model: str = DEFAULT_LLM_MODEL
    llm_base_url: str = ""

    @field_validator("agentic_adapter", mode="before")
    @classmethod
    def default_agentic_adapter(cls, value: str | None) -> str:
        return _or_default(value, AGENTIC_ADAPTER_LANGGRAPH)

    @field_validator("llm_provider", mode="before")
    @classmethod
    def default_llm_provider(cls, value: str | None) -> str:
        return _or_default(value, DEFAULT_LLM_PROVIDER)

    @field_validator("llm_model", mode="before")
    @classmethod
    def default_llm_model(cls, value: str | None) -> str:
        return _or_default(value, DEFAULT_LLM_MODEL)


# =========================
# State - original fields kept, new control fields added
# =========================
class TravelState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str

    # Supervisor + guardrail state
    guardrail_allowed: bool
    guardrail_reason: str
    selected_agents: list[str]
    trip_constraints: dict[str, Any]
    supervisor_reasoning: str

    # Original specialist results
    flight_results: str
    hotel_results: str
    weather_results: str
    itinerary: str

    # New budget + HITL state
    budget_results: str
    approval_request: str
    approved: bool
    human_feedback: str
    final_response: str

    llm_calls: int
    llm_provider: str
    llm_model: str
    llm_base_url: str
    user_id: str
    user_preferences: dict[str, Any]


class SignupRequest(BaseModel):
    email: str
    password: str
    display_name: str = ""


class SigninRequest(BaseModel):
    email: str
    password: str


class PlaceInterest(BaseModel):
    city: str = ""
    region: str = ""
    postal_code: str = ""
    country: str = ""


class UserPreferencesRequest(BaseModel):
    home_city: str = ""
    home_country: str = ""
    typical_budget: str = ""
    currency: str = "USD"
    travel_style: str = ""
    pace: str = ""
    interests: list[str] = Field(default_factory=list)
    companions: str = ""
    avoid: str = ""
    notes: str = ""
    places: list[PlaceInterest] = Field(default_factory=list)
    event_radius_miles: int = 200
    llm_provider: str = "ollama"
    llm_model: str = ""
    llm_base_url: str = ""


class AreaEventsRequest(BaseModel):
    horizon: Literal["week", "month", "quarter"] = "month"


DELETE_TRAVEL_PLAN_PHRASE = "delete this travel plan"


class DeleteTravelRequest(BaseModel):
    confirmation: str = ""


class PreferenceSkillSections(BaseModel):
    who: str = ""
    home: str = ""
    budget: str = ""
    pace: str = ""
    interests: str = ""
    avoid: str = ""
    notes: str = ""


class PreferenceSkillRequest(BaseModel):
    name: str
    description: str = ""
    sections: PreferenceSkillSections = Field(default_factory=PreferenceSkillSections)


class PreferenceSkillSelectRequest(BaseModel):
    ids: list[str] = Field(default_factory=list)
