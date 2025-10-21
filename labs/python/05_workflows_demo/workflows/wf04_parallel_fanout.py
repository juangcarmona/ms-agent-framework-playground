# workflows/wf03_parallel_fanout.py

from agent_framework import Executor, WorkflowContext, WorkflowBuilder, handler


# --- Fan-out entry node -------------------------------------------------
class FanOutDispatcher(Executor):
    @handler
    async def dispatch(self, text: str, ctx: WorkflowContext[str]) -> None:
        print(f"[FanOutDispatcher] Dispatching '{text}' to parallel branches...")
        # Fan-out: send the same message to multiple downstream executors
        await ctx.send_message(text)  # framework handles multiple outgoing edges


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
    def __init__(self, expected_count: int = 2, id="aggregator"):
        super().__init__(id=id)
        self._results: list[str] = []
        self._expected = expected_count

    @handler
    async def collect(self, text: str, ctx: WorkflowContext[str]) -> None:
        self._results.append(text)
        print(f"[AggregatorExecutor] Received {len(self._results)}/{self._expected}")
        if len(self._results) == self._expected:
            merged = " | ".join(self._results)
            print(f"[AggregatorExecutor] Aggregated -> {merged}")
            await ctx.yield_output(merged)


# --- Workflow definition ------------------------------------------------
def build_parallel_fanout_workflow() -> WorkflowBuilder:
    dispatcher = FanOutDispatcher(id="dispatcher")
    upper = UpperCaseExecutor(id="upper")
    reverse = ReverseTextExecutor(id="reverse")
    aggregator = AggregatorExecutor(expected_count=2, id="aggregator")

    workflow = (
        WorkflowBuilder()
        .set_start_executor(dispatcher)
        # fan-out: dispatcher → upper, dispatcher → reverse
        .add_fan_out_edges(dispatcher, [upper, reverse])
        # fan-in: upper → aggregator, reverse → aggregator
        .add_fan_in_edges([upper, reverse], aggregator)
        .build()
    )

    workflow.id = "ParallelFanOut"
    return workflow
