# Architectural Accelerator Framework

This boilerplate template demonstrates the architectural layers and deployment patterns of a modern, multi-agent AI application:
`UX (Streamlit)` ➔ `REST API (FastAPI)` ➔ `Supervisor Agent` ➔ `Child Agents` ➔ `Static Data Layer`

**Key Philosophy:**
This project is explicitly designed as a sandbox and workshop foundation. It is completely *stripped of all external LLM SDKs and live API calls*. It uses a static data layer (`agent_responses.json`) to simulate inference responses instantaneously, allowing developers to focus entirely on learning the architectural patterns (Dependency Injection, OpenTelemetry, Orchestration) without worrying about API keys, tokens, or latency.

---

## 🏗️ Core Architecture & Features

*   **FastAPI & Dependency Injection:** The backend utilizes FastAPI with manual DI (`src/app/main.py`) to inject concrete agent implementations, routing services, and statestores into the lifecycle.
*   **Agentic Orchestration:** The `Supervisor` agent receives frontend queries, manages conversation history (via `InMemoryAgentStateStore`), and executes fan-out queries to `ChildAgentA` and `ChildAgentB`, aggregating their static responses.
*   **OpenTelemetry & Observability:** A robust telemetry layer (`telemetry_service.py`) automatically instruments the FastAPI app, attaching distributed Trace Spans and correlating Python error logs to Azure Application Insights.

---

## 🛠️ Setup Instructions (Automated)

This project uses an isolated Python virtual environment (`.venv`) to encapsulate dependencies and ensure no global environment pollution.

**To initialize the project, run the automated setup script for your OS:**

*   **Windows (PowerShell):**
    ```powershell
    .\configure\setup.ps1
    ```
*   **Mac / Linux (Bash):**
    ```bash
    bash ./configure/setup.sh
    ```

*Note: These scripts automatically detect a valid Python (3.10+) installation, create the hidden `.venv` directory, and securely execute `pip install -r requirements.txt` within it.*

---

## 🚀 Running the Application

You do not need to launch the components manually. The project includes cross-platform `.sh` execution scripts that gracefully handle virtual environment activation, port-conflict detection (`netstat`/`taskkill`), and simultaneous process launching.

### Method A: VS Code Tasks (Recommended)
If using VS Code, press `Ctrl+Shift+B` (or open the Tasks menu) and run the default **Start All** task. This will split the terminal and launch the backend and frontend scripts natively.

### Method B: Bash Execution Scripts
If you prefer running directly from Git Bash or a Unix terminal:

```bash
# Start both the Backend (FastAPI) and Frontend (Streamlit) together
bash src/scripts/start-app.sh

# Or, start them individually:
bash src/scripts/start-backend.sh
bash src/scripts/start-frontend.sh
```

**Accessing the Application:**
*   **Streamlit UI**: `http://localhost:8501`
*   **FastAPI Swagger Docs**: `http://localhost:8010/docs`

---

## 📁 Project Layout

*   `configure/`: OS-specific environment setup scripts.
*   `src/scripts/`: Operational Bash (`.sh`) scripts for application execution and environment activation (`activate-venv.sh`).
*   `src/app/`: The FastAPI Backend Service.
    *   `main.py`: Entrypoint, bootstrapper, and Dependency Injection container.
    *   `api/routes.py`: API endpoints.
    *   `agents/`: Implementations of the `Supervisor` and static `ChildAgents`.
    *   `data/`: Contains `agent_responses.json` containing the simulated LLM completions.
    *   `observability/`: OpenTelemetry setup and configuration.
    *   `state/`: Persistence mechanisms for conversation histories.
*   `src/ui/`: The Streamlit Frontend Service.
