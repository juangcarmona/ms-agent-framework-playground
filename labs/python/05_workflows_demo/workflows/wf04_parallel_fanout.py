from agent_framework import Executor, WorkflowContext, WorkflowBuilder, handler

# --- Fan-out entry node -------------------------------------------------
class FanOutDispatcher(Executor):
    @handler
    async def dispatch(self, text: str, ctx: WorkflowContext[str]) -> None:
        print(f"[FanOutDispatcher] Dispatching '{text}' to parallel branches...")
        await ctx.send_message(text)

# --- Branch 1 -----------------------------------------------------------
class UpperCaseExecutor(Executor):
    @handler
    async def to_upper(self, text: str, ctx: WorkflowContext[str]) -> None:
        result = text.upper()
        print(f"[UpperCaseExecutor] -> {result}")
        await ctx.send_message(result)

# --- Branch 2 -----------------------------------------------------------
class ReverseTextExecutor(Executor):
    @handler
    async def reverse(self, text: str, ctx: WorkflowContext[str]) -> None:
        result = text[::-1]
        print(f"[ReverseTextExecutor] -> {result}")
        await ctx.send_message(result)

# --- Aggregator ---------------------------------------------------------
class AggregatorExecutor(Executor):
    """
    Proper fan-in aggregator: receives a list[str] built automatically by the framework
    when multiple incoming edges converge.
    """
    @handler
    async def aggregate(self, results: list[str], ctx: WorkflowContext[str]) -> None:
        print(f"[AggregatorExecutor] Received all branch results: {results}")
        merged = " | ".join(results)
        print(f"[AggregatorExecutor] Aggregated -> {merged}")
        await ctx.yield_output(merged)

# --- Workflow definition ------------------------------------------------
def build_parallel_fanout_workflow() -> WorkflowBuilder:
    dispatcher = FanOutDispatcher(id="dispatcher")
    upper = UpperCaseExecutor(id="upper")
    reverse = ReverseTextExecutor(id="reverse")
    aggregator = AggregatorExecutor(id="aggregator")

    workflow = (
        WorkflowBuilder()
        .set_start_executor(dispatcher)
        # fan-out: dispatcher → upper, dispatcher → reverse
        .add_fan_out_edges(dispatcher, [upper, reverse])
        # fan-in: collect both results into list[str]
        .add_fan_in_edges([upper, reverse], aggregator)
        .build()
    )

    workflow.id = "04ParFanOut"
    return workflow
