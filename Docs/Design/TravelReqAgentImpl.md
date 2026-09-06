# Travel request path

The three sequences below are also in the root [README.md](../../README.md). This page is the place for more diagrams and layer notes as the graph grows.

A Generate Draft click is three hops: **browser to the planner service**, **service to graph agents**, **one agent to the LLM provider**. `TravelRequest` / `TravelReqCtx` stay on the travel side. LangGraph nodes wrap those in `LLMRequest` / `LLMReqCtx` only when they call a vendor.

Today `TravelRequestAgentImpl` copies `request.message` onto `ctx.user_message`. The adapter-factory hop in diagram 2 is the next `execute` target.

## 1. User to browser to `app.py` to the planner service

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Browser UI
    participant App as app.py
    participant Factory as ServicesObjectFactory
    participant Svc as TravelPlannerService

    User->>UI: Type prompt, Generate Draft
    UI->>App: POST /api/v1/travel/planner
    Note over UI,App: TravelRequest(message, thread_id)
    App->>App: resolve_thread_id
    App->>App: TravelReqCtx(thread_id)
    App->>Factory: get_service(SERVICE_TRAVEL_PLANNER)
    Factory-->>App: TravelPlannerServiceImpl
    App->>Svc: execute(request, ctx)
    Svc-->>App: ResponseCode
    App-->>UI: TravelResponse
    UI-->>User: prompt + plan panel
```

`app.py` talks only to the `TravelPlannerService` interface. Approve is the same `execute` via `POST /api/v1/travel/approve`.

## 2. Planner service to adapter factory to agents

```mermaid
sequenceDiagram
    autonumber
    participant Svc as TravelPlannerServiceImpl
    participant Agents as AgentsObjectFactory
    participant Core as TravelRequestAgentImpl
    participant Adapters as AgenticAdapterObjectFactory
    participant Graph as TravelPlannerLangGraphAdapter
    participant Super as supervisor_agent
    participant Others as specialist agents

    Svc->>Agents: get_agent(AGENT_TRAVEL_REQUEST)
    Agents-->>Svc: TravelRequestAgentImpl
    Svc->>Core: execute(request, ctx)
    Core->>Core: ctx.user_message = request.message
    Core->>Adapters: get_agentic_adapter(travel_planner_langgraph)
    Adapters-->>Core: TravelPlannerLangGraphAdapter
    Core->>Graph: execute(request, ctx)
    Graph->>Super: START to supervisor
    Super-->>Graph: selected_agents
    Graph->>Others: route_from_supervisor
    Others-->>Graph: specialist fields
    Graph-->>Core: ResponseCode
    Core-->>Svc: ResponseCode
```

`TravelPlannerLangGraphAdapter` is one `AgenticFrameworkAdapter`. A later ADK or Strands adapter would register on the same factory.

## 3. `supervisor_agent` to the LLM provider

```mermaid
sequenceDiagram
    autonumber
    participant Super as supervisor_agent
    participant Util as llm_text
    participant Factory as LLMProviderObjectFactory
    participant Groq as GroqLLMProvider
    participant API as Groq API

    Super->>Super: LLMRequest(messages, provider)
    Super->>Super: LLMReqCtx(request)
    Super->>Util: llm_text(request, ctx)
    Util->>Factory: get_provider(request)
    Factory->>Groq: GroqLLMProvider(request)
    Factory-->>Util: LLMProvider
    Util->>Groq: complete(request, ctx)
    Groq->>API: chat.completions.create
    API-->>Groq: text, usage, tool_calls
    Groq-->>Util: LLMResponse + LLMStats
    Util-->>Super: response.text
    Super->>Super: json_from_llm, pick agents
```

Unset `LLMRequest.provider` defaults to Groq. `get_provider` uses `request.config` (model and the rest) from the caller.

## Layers

| Layer | Module | Role |
| --- | --- | --- |
| UI | `portals/your-next-travel-app` | Angular portal: auth, dashboard, planner, preferences |
| App | `app.py` | API only: auth, preferences, planner, approve, catalog |
| Service | `core/services/interfaces.py`, `impl/planner_impl.py` | `TravelPlannerService.execute` |
| Core agent | `core/agents/impl/travel_req_agent.py` | Normalize the user message; hand off to an adapter |
| Agentic adapter | `adapters/agentic/objects.py`, `langgraph/travel_planner.py` | Factory → compiled graph |
| Graph agents | `adapters/agentic/langgraph/agents/` | Supervisor, specialists, HITL, final |
| LLM adapter | `adapters/llm_providers/` | `LLMProvider.complete` (Groq default) |
