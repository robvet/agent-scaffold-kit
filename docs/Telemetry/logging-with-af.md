(1) Emitting logs to console:

One line in main.py, before setup_telemetry():

This adds a StreamHandler (console) to the root logger at INFO level. Then when setup_telemetry() runs, it adds the OpenTelemetry handler on top of that. So every logging.info(...), logging.error(...), and logging.exception(...) call goes to both console and App Insights.

Think of it like C#: basicConfig is adding Console.WriteLine as a log sink, and the telemetry handler is adding Application Insights as a second sink. Both fire.

(2) Agent Framework telemetry hooks:

You're almost certainly right. The Agent Framework likely has its own OpenTelemetry instrumentation — spans for agent invocations, token usage, model calls, etc. Most Python AI frameworks ship with an instrumentation module or at least emit spans under a known tracer name.

To find out what's available, you'd check:

Whether agent_framework has an opentelemetry or instrumentation submodule (like opentelemetry-instrumentation-agent-framework)
What spans it emits by temporarily enabling verbose tracing
But investigating that and wiring it in is a separate task — it would mean changes to telemetry_service.py and possibly new dependencies. I'd recommend we treat that as a future item and not mix it into the current fixes.


https://learn.microsoft.com/en-us/agent-framework/agents/observability?pivots=programming-language-python

