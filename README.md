# Agent Scaffold Kit — Architectural Accelerator

A Python template to accelerate building agentic apps. Skip the boilerplate — the infrastructure is already wired.

**High-level flow:**
`UX (Streamlit)` ➔ `REST API (FastAPI)` ➔ `Supervisor Agent` ➔ `Child Agents` ➔ `Tools` ➔ `LLM / Services`

---

## Why this exists

Building an agentic app from scratch means wiring the same infrastructure over and over: LLM configuration, DI containers, observability, agent patterns, state stores, startup scripts. This template does that work for you.

Clone it, fill in your `.env`, and start building your specific logic immediately.

---

## What's included

| Layer | What's pre-built |
|---|---|
| **Orchestration** | `SupervisorAgent` — fans out to child agents, aggregates results |
| **Agent A (Tool Demo)** | `ChildAgentA` — calls `DatetimeTool` (zero dependencies, shows the tool pattern) |
| **Agent B (LLM Demo)** | `ChildAgentB` — calls `LlmTool` → Azure OpenAI GPT (swap provider by changing the tool) |
| **Tools** | `DatetimeTool`, `LlmTool` — encapsulate capabilities so agents stay thin |
| **LLM Providers** | GPT (default), Gemini, Anthropic, Grok, DeepSeek — all wired, providers commented in for easy swap |
| **Memory (Strategy Pattern)** | `IAgentStateStore` interface + `InMemoryAgentStateStore` — swap for Redis/SQL by implementing the interface |
| **Config** | `Settings` (Pydantic) — loads all LLM keys and timeouts from `.env` |
| **Identity** | `AzureIdentityProvider` — `DefaultAzureCredential` for keyless Azure auth |
| **Observability** | OpenTelemetry traces + Azure Application Insights support via `TelemetryService` |
| **API** | FastAPI + manual DI wiring in `main.py` |
| **UI** | Streamlit chat interface with model selection, dark theme, copy/export |

---

## Prerequisites

- Python **3.10+**
- Git Bash (Windows) or Bash (macOS/Linux)
- VS Code (optional, for task-based launching)

---

## Quickstart

### 1) Configure environment

Copy `.env.example` to `.env` and fill in your Azure OpenAI values (required) and optionally Gemini, Anthropic, etc.:

```bash
cp .env.example .env
```

### 2) Setup (creates `.venv` + installs deps)

**Windows (PowerShell):**
```powershell
.\configure\setup.ps1
```

**Mac / Linux (Bash):**
```bash
bash ./configure/setup.sh
```

### 3) Run

**Option A: VS Code Tasks (recommended)**
- Press `Ctrl+Shift+B` → run **Start All**

**Option B: Shell scripts**
```bash
bash src/scripts/start-app.sh        # Backend + Frontend together
bash src/scripts/start-backend.sh    # Backend only  (port 8010)
bash src/scripts/start-frontend.sh   # Frontend only (port 8501)
```

### 4) Open

- **Streamlit UI:** `http://localhost:8501`
- **FastAPI Swagger:** `http://localhost:8010/docs`

---

## Swapping the LLM Provider

To use Gemini instead of GPT for `ChildAgentB`:
1. Add a `GeminiTool` in `src/app/tools/` following the same pattern as `llm_tool.py`
2. In `child_agent_b.py`, replace `self._tool = LlmTool()` with `self._tool = GeminiTool()`
3. Fill in `GEMINI_API_KEY` in `.env`

The agent code does not change — only the tool.

Pre-built agent files (ready to use): `gpt_agent.py`, `gemini_agent.py`, `anthropic_agent.py`, `grok_agent.py`, `deepseek_agent.py`

---

## Swapping the Memory Store

The memory layer uses the **Strategy Pattern**:
- `IAgentStateStore` — the interface (contract)
- `InMemoryAgentStateStore` — the default (local in-process)

To use Redis or SQL: implement `IAgentStateStore`, then inject your implementation in `main.py`. Nothing else changes.

---

## Project Layout

```
configure/               OS-specific setup scripts
src/
  scripts/               Bash run scripts + venv activation
  app/
    main.py              FastAPI entrypoint + DI wiring
    api/routes.py        REST endpoints
    agents/              Supervisor + child agents + all LLM provider agents
    tools/               DatetimeTool, LlmTool (add your tools here)
    config/              Settings (Pydantic), ModelConfig
    identity/            AzureIdentityProvider (DefaultAzureCredential)
    observability/       TelemetryService (OpenTelemetry)
    state/               IAgentStateStore + InMemoryAgentStateStore
    prompts/             Jinja2 prompt templates
    models/              Pydantic request/response models
    data/                agent_responses.json (kept for testing)
  ui/
    streamlit_app.py     Chat UI with model selection + dark theme
```

---

## Troubleshooting

- **Ports in use:** Scripts auto-kill processes on ports `8010`/`8501` using `netstat`/`taskkill`.
- **Azure auth:** For local dev, run `az login` first. In production, use Managed Identity.
- **No LLM response:** Verify `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_DEPLOYMENT_GPT` are set in `.env`.
