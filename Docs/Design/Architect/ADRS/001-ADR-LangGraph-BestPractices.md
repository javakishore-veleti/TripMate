# ADR 001 — LangGraph best practices for trip compose

- **Status:** Accepted
- **Date:** 2026-09-06
- **Scope:** `TripComposeAdapter` and the travel request graph under `middleware/adapters/agentic/langgraph/`

## Context

Trip compose is a multi-node LangGraph: intake, coordinator, specialists, draft, traveler review, and final assemble. It pauses for human approval, then resumes on the same thread. Without explicit operating rules, the graph can loop, lose typed constraints, crash on a specialist error, or resume a review without a clear snapshot of what the traveler is approving.

This ADR records the practices the trip graph must follow.

## Decision

Adopt the practices below for the trip compose graph. Feature modules stay on facade → service → adapter factory. Services do not import LangGraph.

## Practices

### 1. Keep graph state typed

`TravelState` is a `TypedDict` of known fields only. Domain results (`flight_results`, `itinerary`, …) sit beside operational fields (`current_step`, `step_count`, `max_steps`, `error_count`, `last_error`, `proposed_action`). Nodes write those keys; they do not invent ad-hoc bags.

### 2. Validate and normalize constraints

Coordinator output is cleaned through `normalize_constraints` against `empty_constraints()`. Unknown keys are dropped. Lists and strings are coerced. `start_date` stays in the constraint shape so later nodes can rely on it.

### 3. Give every node a runtime wrapper

Every graph node is registered as `with_runtime(name, fn)`. The wrapper increments `step_count`, records `current_step`, and catches uncaught exceptions so one specialist failure does not tear down the run.

### 4. Bound the cycle

`max_steps` defaults to 16. When the count exceeds the limit, the wrapper marks the state halted and routing sends the run to `HALT` → `END`. Draft also routes through `route_after_draft` so a halted draft does not enter traveler review.

### 5. Degrade on error instead of crashing

Specialists catch their own failures with `brief_failure` and continue with a short `last_error`. The runtime wrapper is the backstop for anything they miss. The traveler still gets a usable note rather than a raw stack.

### 6. Pause for review with an explicit snapshot

Draft writes `proposed_action` (what the traveler is being asked to approve). Traveler review interrupts with that snapshot. Approve / reject resumes the same compiled graph via `Command(resume=…)` on the same `thread_id`.

### 7. Checkpoint by thread, keep existing ids

The compiled graph uses a durable checkpointer (SQLite in the app database, or Postgres when configured). `graph_config` sets `thread_id` from `TravelReqCtx` and `checkpoint_ns` to `""` so in-flight drafts keep working. Thread ids stay the client stamp; they are not rewritten into a new namespace scheme.

### 8. Route on explicit maps

Conditional edges use named routers (`route_after_intake`, `route_from_coordinator`, `route_after_specialist`, `route_after_draft`) and a shared `ROUTE_MAP`. Halted state always leaves the cycle. Unrelated asks go to `REQUEST_DECLINED` → `END`.

### 9. Hide graph internals from the traveler

Pipeline copy maps `__interrupt__` to a traveler-facing line and skips other `__*` node names. Resume starts with a polish line, not a LangGraph token.

### 10. Prove the routers

Route, halt, constraint, and step-bound behavior is covered by unit tests in `middleware/adapters/agentic/langgraph/tests/test_routes.py`.

## Out of scope

These are not required for this graph:

- External tracing or observability platforms
- Parallel fan-out of specialists
- Renaming `thread_id` to a tenant/user/session scheme
- Extra retry or fallback edges beyond degrade-and-continue
- A full integration-test suite for every node

## Consequences

- New trip-graph nodes must use `with_runtime`, write typed `TravelState` keys, and route halt the same way.
- Changing `thread_id` format or `checkpoint_ns` is a breaking change for saved drafts.
- Feature services remain LangGraph-free; only the adapter layer owns the graph.
