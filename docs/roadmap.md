# Model Fusion Playground - Roadmap

## Current Status

- **Telemetry:** HTTP instrumentation added to show LLM API calls as dependencies in Application Insights

## Completed Features

### Copy resonpses to clipboard

## Upcoming Features

### Enhanced Telemetry (Next)

Add token counts, model latency metrics, success rates, and custom Azure Workbook.

Deeper error telemetry to App Insights

Update ModelResponse with input_tokens, output_tokens, processing_time_ms
Modify each agent to parse tokens from API response and track time
Update frontend to show GPT |

**Value:**

- Token usage tracking per model
- Latency comparison dashboards
- Success/error rate monitoring
- Demo-ready visualizations

**Technical:**

- Parse API responses for token usage (input/output tokens)
- Add custom metrics: `model_latency_ms`, `model_call_result`
- Set span attributes: `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`
- Create Azure Workbook JSON template

---

### Add image upload

### Prompt Editing and Persistence (Active - Tomorrow)

- [ ] Add "Edit System Prompt" link to the Model Consensus header
- [ ] Implement "Prompt Library" Modal for managing (Add/Edit/Remove) complex prompts
- [ ] Build JSON-based persistence layer for the prompt library
- [ ] (Future) Sync prompts to Azure Blob Storage

---

### Streaming Responses

Stream LLM responses in real-time to the UI instead of waiting for full completion.

**Value:**

- Perceived speed improvement
- Visual demo impact - 5 models "racing" simultaneously
- Better UX - user can read while generation continues

**Technical:**

- Enable `stream=True` in agent API calls
- Add WebSocket or SSE endpoint
- Update Streamlit to display streaming tokens

---

### Live Logging Popup

Real-time log viewer in Streamlit for debugging and demos.

**Value:**

- Visual feedback during execution
- Debugging without terminal access
- Impressive for technical demos

**Technical:**

- Reuse WebSocket infrastructure from streaming
- Send log events to Streamlit popup on demand

---

### Group Chat / Debate Mode

Agent debate over disagreements using Semantic Kernel for orchestration.

**Value:**

- Showcase different model perspectives
- Consensus-building through multi-round debate
- Interesting demo for AI decision-making

**Technical:**

- Semantic Kernel as debate orchestrator
- Independent agents remain unchanged
- Configurable debate rounds and consensus detection
