# Supervisor Design

The Supervisor should be a thin orchestrator that delegates to specialists — exactly like a C# Controller should delegate to Services. The problem with supervisor maps directly to the Single Responsibility Principle (the S in SOLID).  Supervisor is a "God class." It knows too much, does too much. When one thing changes, the God class can break in multiple places because it owns too many concerns. 

Consider the risks:

| Risk | Example |
|---|---|
| Fragile modifications | Adding a third mode (e.g., "ranking") means modifying the same class that handles search, debate, state, and aggregation. One typo in the new mode could break the existing two. |
| Untestable | You can't unit test state management without also setting up agents, aggregation, and telemetry. In C# terms — you'd need to mock 5 dependencies just to test one behavior. |
| Merge conflicts | Two developers working on different features (one on debate logic, one on state persistence) are editing the same file, same class. |
| Hidden coupling | The debate round logic silently depends on how `_call_agent` maps exceptions. Change the error format in one place, the other quietly breaks. |
| Duplication drift | The copy-pasted patterns in `query()` and `_run_debate()` will diverge over time — someone fixes a bug in one path but forgets the other. |
| Violates Open/Closed | Adding functionality requires modifying the Supervisor instead of extending it with a new strategy class. Every modification risks regressions. |

## What the Supervisor Currently Owns
The Supervisor class is doing at least 5 distinct jobs:

Responsibility	Where	C#/Java Analogy

| # | Responsibility | Where | C#/Java Analogy |
|---|---|---|---|
| 1 | Conversation ID lifecycle | `query()` lines generating UUID, threading it through | A `ConversationManager` or middleware |
| 2 | State hydration + persistence | Load state for all agents, append history, save state — duplicated in both `query()` and `_run_debate()` | A `UnitOfWork` or `StateManager` |
| 3 | Agent filtering | Parsing `enabled_agents`, handling the `["string"]` Swagger quirk, fallback logic | An `AgentResolver` or filter service |
| 4 | Execution strategy | Search-mode fan-out vs. debate-mode multi-round loop — two completely different algorithms crammed into one class | Strategy Pattern — `IExecutionStrategy` with `SearchStrategy` and `DebateStrategy` |
| 5 | Result mapping | Converting `asyncio.gather` exceptions into `ModelResponse(status="error")` — duplicated in both `query()` and `_run_debate()` | A `ResultMapper` or response builder |

The only thing the Supervisor should own is the orchestration decision: "given this request, pick a strategy, execute it, return the response."

## The Smell: Duplicated Patterns
The clearest signal is the copy-paste between query() (search mode) and _run_debate():

Both do fan-out with asyncio.gather + _call_agent
Both map exceptions to ModelResponse
Both save state with the same loop
Both call self._aggregation_tool.aggregate() at the end

In C# terms, this is like having a Controller that contains the business logic for two different workflows inline, instead of calling into service classes.

## What a Refactored Version Would Look Like

Think of it like a C# Mediator or Orchestrator:

Supervisor.query()              ← thin: resolve strategy, delegate, return
  │
  ├── AgentResolver.resolve()   ← which agents are active?
  ├── StateManager.hydrate()    ← load conversation state
  ├── IExecutionStrategy.execute()
  │     ├── SearchStrategy      ← single fan-out + aggregate
  │     └── DebateStrategy      ← multi-round loop + aggregate
  ├── StateManager.persist()    ← save conversation state
  └── return SupervisorResponse

  _call_agent would become an AgentInvoker class — owns the timeout, prompt rendering, and telemetry span creation. Both strategies would use it.

## The Tradeoff (Honest Assessment)
For a demo/teaching app, the current design is functional and readable top-to-bottom. Extracting 4-5 new classes adds indirection that can obscure the flow for someone learning the pattern.

But if this were production code or the codebase were growing (new modes, new agent types, retry policies), the current Supervisor would become a "God class" fast. The duplicated logic between search and debate is already the early warning sign.

Bottom line: Your instinct is correct. The Supervisor should be a thin orchestrator that delegates to specialists — exactly like a C# Controller should delegate to Services. The question is whether the demo benefits from that discipline now or if you'd prefer to keep it flat for teaching purposes.

## Supervisor Modernization: Microsoft Agent Framework

The app will implement a sequential workflow that contains a parallel stage:

- Resolve request/context (mode, enabled agents, conversation state)
- Build prompts
- Fan-out to model agents in parallel
- Fan-in collect/normalize results
- Aggregate/synthesize
- Persist state and return response

So it is not "purely parallel" and not "purely sequential." It is a pipeline (sequential orchestration) with a parallel inference block in the middle.

For your app:
