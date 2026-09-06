# Travel request path

The sequences below are also in the root [README.md](../../README.md). This page is the place for more diagrams as the trip compose graph grows.

A Generate Draft click is three hops: **browser to the planner service**, **service to the compose graph**, **one specialist to the LLM provider**. `TravelRequest` / `TravelReqCtx` stay on the travel side. Graph nodes wrap those in `LLMRequest` / `LLMReqCtx` only when they call a model.

Today `TravelRequestAgentImpl` copies `request.message` onto `ctx.user_message`. The adapter factory in diagram 2 is the `execute` target.

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

## 2. Planner service to adapter factory to specialists

```mermaid
sequenceDiagram
    autonumber
    participant Svc as TravelPlannerServiceImpl
    participant Agents as AgentsObjectFactory
    participant Core as TravelRequestAgentImpl
    participant Adapters as AgenticAdapterObjectFactory
    participant Graph as TripComposeAdapter
    participant Intake as intake
    participant Coord as coordinator
    participant Others as specialists

    Svc->>Agents: get_agent(AGENT_TRAVEL_REQUEST)
    Agents-->>Svc: TravelRequestAgentImpl
    Svc->>Core: execute(request, ctx)
    Core->>Core: ctx.user_message = request.message
    Core->>Adapters: get_agentic_adapter(langgraph)
    Adapters-->>Core: TripComposeAdapter
    Core->>Graph: execute(request, ctx)
    Graph->>Intake: START to intake
    Intake-->>Graph: request_accepted
    Graph->>Coord: coordinator
    Coord-->>Graph: selected_specialists
    Graph->>Others: air, stay, climate, cost, draft
    Others-->>Graph: specialist fields
    Graph-->>Core: ResponseCode
    Core-->>Svc: ResponseCode
```

`TripComposeAdapter` is one `AgenticFrameworkAdapter`. A later ADK or Strands adapter would register on the same factory.

## 3. Coordinator to the LLM provider

```mermaid
sequenceDiagram
    autonumber
    participant Coord as coordinator
    participant Util as llm_text
    participant Factory as LLMProviderObjectFactory
    participant Groq as GroqLLMProvider
    participant API as Groq API

    Coord->>Coord: LLMRequest(messages, provider)
    Coord->>Coord: LLMReqCtx(request)
    Coord->>Util: llm_text(request, ctx)
    Util->>Factory: get_provider(request)
    Factory->>Groq: GroqLLMProvider(request)
    Factory-->>Util: LLMProvider
    Util->>Groq: complete(request, ctx)
    Groq->>API: chat.completions.create
    API-->>Groq: text, usage, tool_calls
    Groq-->>Util: LLMResponse + LLMStats
    Util-->>Coord: response.text
    Coord->>Coord: json_from_llm, pick specialists
```

Unset `LLMRequest.provider` defaults to the catalog default (Ollama locally). `get_provider` uses `request.config` from the caller.

## Layers

| Layer | Module | Role |
| --- | --- | --- |
| UI | `portals/your-next-travel-app` | Angular portal: auth, dashboard, planner, preferences |
| App | `app.py` | API only: auth, preferences, planner, approve, catalog |
| Service | `core/services/interfaces.py`, `impl/planner_impl.py` | `TravelPlannerService.execute` |
| Core agent | `core/agents/impl/travel_req_agent.py` | Normalize the user message; hand off to an adapter |
| Agentic adapter | `adapters/agentic/objects.py`, `langgraph/trip_compose.py` | Factory → compiled trip compose graph |
| Specialists | `adapters/agentic/langgraph/specialists/` | Intake, coordinator, research, traveler review, assemble |
| LLM adapter | `adapters/llm_providers/` | `LLMProvider.complete` |
