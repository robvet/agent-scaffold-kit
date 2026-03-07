# Specialized Model Prompting — Architectural Overview

## Problem

In a multi-model fusion system, all models originally received identical system prompts. While functional, this approach leaves performance on the table — each model has distinct strengths and responds optimally to different prompting styles. A one-size-fits-all prompt cannot exploit those differences.

## Solution: Dynamic System Prompts via Strategy Pattern

Rather than maintaining separate prompt files per model (which violates DRY and creates maintenance drift), we use a **single Jinja2 template** (`src/app/prompts/system-prompt.jinja2`) that generates model-specific system prompts at runtime.

### Architecture (C#/Java Analogy)

Think of this as the **Strategy Pattern**:

- **Interface**: The shared base instructions (common to all models)
- **Concrete Strategies**: Model-specific guidance blocks (one per model)
- **Context**: Each agent's `create_af_agent()` method, which selects the strategy via `model_name`

```
ISystemPromptStrategy<TModel>
├── SharedBaseInstructions          ← "interface contract"
├── GPTStrategy                     ← structured, step-by-step
├── ClaudeStrategy                  ← nuanced, multi-perspective
├── GeminiStrategy                  ← concise, factual
├── DeepSeekStrategy                ← reasoning chain, show-your-work
└── GrokStrategy                    ← conversational, direct
```

Resolved at runtime:
```python
# In each agent's create_af_agent() method
instructions = prompt_loader.render("system-prompt.jinja2", model_name="gpt")
```

### Template Structure

```
┌─────────────────────────────────────────┐
│  Shared Base Instructions               │  ← All models get this
│  "You are a knowledgeable AI assistant   │
│   in a multi-model fusion system..."     │
├─────────────────────────────────────────┤
│  Model-Specific Block (conditional)      │  ← Only the matching block renders
│  {% if model_name == "gpt" %}            │
│    ...GPT-specific guidance...           │
│  {% elif model_name == "claude" %}       │
│    ...Claude-specific guidance...        │
│  {% endif %}                             │
├─────────────────────────────────────────┤
│  Shared Closing Instructions             │  ← All models get this
│  "Stay on topic... Do not identify       │
│   yourself by name or provider..."       │
└─────────────────────────────────────────┘
```

### Call Flow

```
User submits prompt
        │
        ▼
Supervisor fans out to all agents in parallel
        │
        ├── GPTAgent.create_af_agent()
        │     └── render("system-prompt.jinja2", model_name="gpt")
        │           └── Returns: base + GPT block + closing
        │
        ├── AnthropicAgent.create_af_agent()
        │     └── render("system-prompt.jinja2", model_name="claude")
        │           └── Returns: base + Claude block + closing
        │
        ├── GeminiAgent.create_af_agent()
        │     └── render("system-prompt.jinja2", model_name="gemini")
        │           └── Returns: base + Gemini block + closing
        │
        ├── DeepSeekAgent.create_af_agent()
        │     └── render("system-prompt.jinja2", model_name="deepseek")
        │           └── Returns: base + DeepSeek block + closing
        │
        └── GrokAgent.create_af_agent()
              └── render("system-prompt.jinja2", model_name="grok")
                    └── Returns: base + Grok block + closing
```

**Key point**: The user's raw prompt is never modified. The system prompt shapes how each model *interprets* the same user input.

## Model-Specific Prompting Needs

### GPT-4 (OpenAI)

**Strength**: Instruction following, structured output, format compliance.

**Prompting needs**: GPT-4 excels when given explicit formatting instructions. It responds well to directives like "use headers," "use bullet points," and "step-by-step." Without this guidance, GPT-4 tends to produce competent but generic prose. With it, the output becomes highly organized and scannable.

**System prompt guidance**:
> Structure your response with clear headers and bullet points where appropriate. Use step-by-step reasoning to build toward your conclusion. Favor explicit formatting to make your answer scannable.

### Claude (Anthropic)

**Strength**: Nuance, safety-consciousness, long-form reasoning, balanced analysis.

**Prompting needs**: Claude produces its best work when encouraged to think deeply rather than respond quickly. It thrives with prompts that ask it to consider multiple angles, acknowledge complexity, and weigh tradeoffs. Without this, Claude can default to overly cautious, hedge-heavy responses. With the right nudge, it delivers thoughtful analysis.

**System prompt guidance**:
> Think through this carefully before answering. Consider nuance, edge cases, and multiple perspectives. When the topic is complex, acknowledge tradeoffs rather than oversimplifying.

### Gemini (Google)

**Strength**: Multimodal capability, factual grounding, conciseness.

**Prompting needs**: Gemini tends to be verbose when given open-ended prompts. It performs best when directed to be concise and factual. Its strength is in quick, accurate, grounded answers — and the system prompt should reinforce that rather than encourage lengthy elaboration.

**System prompt guidance**:
> Be concise and factual. Prioritize accuracy and directness. Get to the point quickly and avoid unnecessary elaboration.

### DeepSeek

**Strength**: Code generation, mathematical reasoning, logical analysis.

**Prompting needs**: DeepSeek shines when asked to show its work. For technical and analytical queries, it produces stronger results when prompted to explain its reasoning chain before delivering the answer. This "think aloud" style matches its training emphasis on chain-of-thought reasoning.

**System prompt guidance**:
> Show your reasoning chain. For technical or analytical topics, explain your approach before presenting the answer. Walk through the logic step by step.

### Grok (xAI)

**Strength**: Conversational tone, directness, less filtered responses.

**Prompting needs**: Grok's differentiator is its natural, conversational style. Over-formalizing the system prompt fights against this strength. The prompt should encourage directness and a natural voice while maintaining thoroughness — letting Grok be Grok.

**System prompt guidance**:
> Be direct and conversational. Don't over-formalize your response. Answer naturally while still being thorough.

## Design Decisions

### Why not separate system prompt files?

Maintaining five `.txt` files with duplicated base instructions creates maintenance drift. When the shared framing changes (and it will), you'd need to update all five files identically. A single Jinja2 template keeps the shared contract in one place.

### Why not a dedicated rewrite agent?

A rewrite agent would add a sequential step before the parallel fan-out, introducing 1-3 seconds of latency. The system prompt approach achieves model-specific behavior at zero latency cost because the prompt is rendered in-memory before the API call.

### Why system prompts and not user prompt rewriting?

The system prompt acts as a persistent frame that shapes how the model interprets *every* user input. The user's raw question flows unchanged to all models. Each model just "wears different glasses" when reading it. This avoids the risk of information loss that comes with rewriting user input.

## Files Involved

| File | Role |
|------|------|
| `src/app/prompts/system-prompt.jinja2` | The dynamic template (Strategy Pattern dispatch) |
| `src/app/utils/prompt_loader.py` | `render()` function that processes the Jinja2 template |
| `src/app/agents/*_agent.py` | Each agent's `create_af_agent()` passes its `model_name` |
| `src/app/prompts/system/model-prompt.txt` | Original static prompt (retained as fallback reference) |