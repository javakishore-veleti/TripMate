# Your Travel Portal (YTP)

Your Travel Portal (YTP) is a self-run travel portal to plan trips with local or cloud LLM models you control. Run YTP on your laptop or on AWS, Azure, GCP, or another cloud you own. You keep the keys and the data. A planning and research site you run or host on your own.

The product name is **Your Next Travel**. FastAPI is the API. The Angular portal lives in `portals/your-next-travel-app`.

This is software you run. Clone the repo or use a container image. The project authors do not host your data.

## Local development

Local only. One command is enough:

```bash
npm run local:app-run
```

That command:

1. Activates this repo's `.venv` if your shell is not already using it
2. Runs `uv sync`
3. Starts FastAPI, which runs Alembic (Liquibase-style) `upgrade head` on every boot
4. Starts the Angular portal after `/health` is ready

- API: `http://127.0.0.1:8000`
- Portal: `http://127.0.0.1:4200`
- Schema-only: `npm run local:schema-setup`
- Local data: `runtime-data/local-deploy/` (SQLite and preference packs; created on this machine, not in git)

Optional: `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`) for a local Ollama provider.

## Table of contents

- [Request flow](#request-flow)
  - [1. User to the API to the planner service](#1-user-to-the-api-to-the-planner-service)
  - [2. Planner service to TravelRequestAgentImpl](#2-planner-service-to-travelrequestagentimpl)
- [Where code lives](#where-code-lives)
- [Understanding Python Frameworks](#understanding-python-frameworks)
  - [Uvicorn Usage](#uvicorn-usage)
    - [How Uvicorn integrates with FastAPI](#how-uvicorn-integrates-with-fastapi)
    - [How Uvicorn finds the app object](#how-uvicorn-finds-the-app-object)
    - [What ASGI stands for and why it matters](#what-asgi-stands-for-and-why-it-matters)
    - [What came before ASGI](#what-came-before-asgi)
    - [ASGI servers and alternatives](#asgi-servers-and-alternatives)
    - [Compared to Tomcat and WebLogic](#compared-to-tomcat-and-weblogic)

## Request flow

What runs **today**. The UI sends `agentic_adapter` (default `langgraph`). The API lives under `middleware/`. Each feature module owns its api, facade, service, and DAOs. LangGraph and LLM providers stay in `middleware/adapters/` so the same module can later use Google ADK. More diagrams are in [Docs/Design/TravelReqAgentImpl.md](Docs/Design/TravelReqAgentImpl.md).

### 1. User to the API to the planner service

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant UI as Browser UI
    participant API as plans_mgmt api
    participant Facade as PlannerFacade
    participant Svc as TravelPlannerService

    User->>UI: Type prompt, Generate Draft
    UI->>API: POST /api/v1/travel/planner
    Note over UI,API: TravelRequest(message, thread_id, agentic_adapter)
    API->>API: resolve_thread_id, TravelReqCtx
    API->>Facade: execute(request, ctx)
    Facade->>Svc: execute(request, ctx)
    Svc-->>Facade: ResponseCode
    Facade-->>API: ResponseCode
    API->>API: result.prompt = ctx.user_message
    API-->>UI: TravelResponse
    UI-->>User: Draft plan for review
```

### 2. Planner service to TravelRequestAgentImpl

```mermaid
sequenceDiagram
    autonumber
    participant Svc as TravelPlannerServiceImpl
    participant Agents as AgentsObjectFactory
    participant Core as TravelRequestAgentImpl
    participant Adapters as AgenticAdapterObjectFactory
    participant Graph as TripComposeAdapter

    Svc->>Agents: get_agent(AGENT_TRAVEL_REQUEST)
    Agents-->>Svc: TravelRequestAgentImpl
    Svc->>Core: execute(request, ctx)
    Core->>Core: ctx.user_message = request.message
    Core->>Adapters: get_agentic_adapter(request.agentic_adapter)
    Adapters-->>Core: TripComposeAdapter
    Core->>Graph: execute(request, ctx)
    Graph-->>Core: SUCCESS
    Core-->>Svc: SUCCESS or SKIP
```

More diagrams (coordinator, LLM provider): [Docs/Design/TravelReqAgentImpl.md](Docs/Design/TravelReqAgentImpl.md).

## Where code lives

| Layer | Path | Role |
| --- | --- | --- |
| UI | `portals/your-next-travel-app` | Angular portal |
| API entry | `middleware/app.py`, `middleware/api/factory.py` | Uvicorn target; mounts module routers |
| Feature module | `middleware/modules/<feature>/` | `api/`, facades, services, `persistence/` (entities + DAOs) |
| Shared factories | `middleware/modules/shared/` | `ServicesObjectFactory`, `DaoObjectFactory` |
| Platform DB | `middleware/persistence/` | Alembic, engine, `Base`, checkpointer |
| Agentic adapters | `middleware/adapters/agentic/` | `TripComposeAdapter` (LangGraph); ADK would register here |
| LLM providers | `middleware/adapters/llm_providers/` | Ollama, Groq |
| Local data | `runtime-data/local-deploy/` | SQLite and preference packs (not in git) |

Call sequence: API → facade → service → DAO and/or adapter factory → LangGraph (or later ADK) → LLM provider.

## Understanding Python Frameworks

FastAPI is the **application** (routes, validation, responses). Uvicorn is the **server** that listens on a host and port and calls that application. They meet through **ASGI**, a standard interface in Python web stacks.

### Uvicorn Usage

Your Next Travel starts the API from `middleware/app.py` with configurable host and port (defaults: `0.0.0.0` and `8000`):

```bash
python -m middleware.app
python -m middleware.app --host 0.0.0.0 --port 9000
```

Or set `HOST` / `PORT` in the environment or a `.env` file. CLI flags override env. The equivalent Uvicorn CLI is:

```bash
uvicorn middleware.app:app --host 0.0.0.0 --port 8000 --reload
```

#### How Uvicorn integrates with FastAPI

Uvicorn and FastAPI are two layers.

- **FastAPI is an ASGI app.** `app = FastAPI(...)` builds an object that implements `async def __call__(scope, receive, send)`. `@app.get` / `@app.post` only register routes on that object. FastAPI does **not** open a socket or listen on a port.
- **Uvicorn is the ASGI server.** `uvicorn.run(...)` binds `host` / `port`, speaks HTTP, and for each request:
  1. Parses the HTTP request into ASGI `scope` / `receive`
  2. Calls `await app(scope, receive, send)`
  3. FastAPI matches the path, runs your handler, builds a response
  4. Uvicorn writes that response back to the client

`if __name__ == "__main__"` means this only runs when you execute `python -m middleware.app`. Importing `app` (tests, or `uvicorn middleware.app:app` on the CLI) creates the FastAPI instance but does not start the server twice.

#### How Uvicorn finds the app object

Uvicorn does not scan the project for FastAPI classes. You point it at **one object** with an import path.

In `middleware/app.py` that argument is `"middleware.app:app"`:

| Part | Meaning in this repo |
| --- | --- |
| Left `middleware.app` | The **module** `middleware/app.py` |
| Right `app` | The **variable** `app = FastAPI(...)` in that module |

Uvicorn does the equivalent of:

```python
import importlib

module = importlib.import_module("middleware.app")  # loads middleware/app.py
asgi_app = getattr(module, "app")                   # the FastAPI() instance
```

Then it only talks to that object. Other classes (`TravelPlannerService`, templates, and so on) are used only because your route functions call them.

With `reload=True`, a parent process watches files. A **child** process imports `"middleware.app:app"` again after a change. That is why reload needs the string. Passing the in-memory `app` object works without reload, but the reloader cannot re-import it.

If you renamed the instance (for example `api = FastAPI(...)`), you would pass `"middleware.app:api"`. If that path is missing or the object is not ASGI-callable, Uvicorn fails — it will not guess another object. The left side stays `middleware.app` because that is the **module** name, not the variable name.

#### What ASGI stands for and why it matters

**ASGI** is **Asynchronous Server Gateway Interface**. It is the contract between a web server (Uvicorn, Hypercorn, Daphne) and a Python web app (FastAPI, Starlette, Django). The server does not need FastAPI internals; the app does not need to know sockets. They agree on one callable:

```python
async def app(scope, receive, send):
    ...
```

- `scope` — request metadata (path, method, headers, type `http` / `websocket` / `lifespan`)
- `receive` — await incoming body / events
- `send` — await outgoing response / events

Python’s older web apps were mostly **sync**: one request occupies one thread or process until it finishes. Modern APIs wait a lot (LLM calls, HTTP, DB, WebSockets). ASGI lets the server **await** those without blocking the whole worker, so one process can handle many concurrent connections. It also standardizes HTTP, WebSockets, and startup/shutdown in one interface.

#### What came before ASGI

**WSGI** (Web Server Gateway Interface, PEP 333 / 3333, ~2003) is the synchronous predecessor:

```python
def app(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/plain")])
    return [b"hello"]
```

Used by Flask, classic Django, and Pyramid. Served by Gunicorn, uWSGI, Waitress, and mod_wsgi.

WSGI is request/response only, **synchronous**, and has no first-class WebSockets or long-lived streams. You can run WSGI apps on ASGI via adapters (`a2wsgi`, `WSGIMiddleware`), but they stay sync underneath.

| | WSGI | ASGI |
| --- | --- | --- |
| Style | sync | async (can still call sync code) |
| Connections | one request, then done | many concurrent, plus WebSockets |
| Typical apps | Flask, classic Django | FastAPI, Starlette, Django (ASGI mode) |
| Typical servers | Gunicorn, uWSGI | Uvicorn, Hypercorn, Daphne |

#### ASGI servers and alternatives

These are ASGI **servers** (alternatives to Uvicorn):

- **Uvicorn** — asyncio; common FastAPI default (what Your Next Travel uses)
- **Hypercorn** — HTTP/1, HTTP/2, HTTP/3; asyncio / Trio / uvloop
- **Daphne** — Django Channels; strong on WebSockets
- **Granian** — Rust-based ASGI/WSGI/RSGI server
- **Gunicorn + Uvicorn workers** — Gunicorn supervises processes; each worker is Uvicorn (common in production)

Related but not ASGI:

- **WSGI** — still fine for sync Flask/Django
- **RSGI** — another Python async app interface (Granian); less common

Because FastAPI speaks ASGI, `"middleware.app:app"` can be served by any ASGI server, not only Uvicorn.

#### Compared to Tomcat and WebLogic

Yes — **same job at a high level**: they accept HTTP (and often WebSockets), then hand the request to your application.

| Java world | Python ASGI world |
| --- | --- |
| Tomcat, Jetty | Uvicorn, Hypercorn, Daphne |
| WebLogic, WebSphere (full app server) | closer to Gunicorn + Uvicorn, or nginx + Uvicorn |
| WAR / servlet (`HttpServlet`) | ASGI app (`FastAPI()` / Django) |
| `web.xml` / servlet mapping | `@app.get`, `@app.post` |

Tomcat and WebLogic are **heavy application servers**: many Java apps, thread pools, JNDI, datasources, sessions, clustering, admin consoles.

Uvicorn, Hypercorn, and Daphne are **slim protocol servers**. They mostly bind a port, speak HTTP/ASGI, and call one Python app. They do not ship a Java-style admin console or JNDI. TLS, process management, and load balancing are usually **nginx/Caddy + Gunicorn/systemd/Docker**.

- **Uvicorn** ≈ a small Tomcat for one FastAPI process
- **WebLogic** ≈ a whole platform (server + ops + extras)
- **Gunicorn with Uvicorn workers** ≈ a production farm: one master, several workers

In Your Next Travel, Uvicorn is the server; FastAPI is the app inside it — like Tomcat hosting one webapp.
