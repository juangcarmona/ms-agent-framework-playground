# workflows/wf01_basic_sequence.py
from agent_framework import Executor, WorkflowContext, WorkflowOutputEvent, WorkflowBuilder, handler


class UpperCaseExecutor(Executor):
    @handler
    async def to_upper(self, text: str, ctx: WorkflowContext[str]) -> None:
        result = text.upper()
        print(f"[UpperCaseExecutor] Input: '{text}' -> '{result}'")
        await ctx.send_message(result)


class ReverseTextExecutor(Executor):
    @handler
    async def reverse(self, text: str, ctx: WorkflowContext[str]) -> None:
        result = text[::-1]
        print(f"[ReverseTextExecutor] Input: '{text}' -> '{result}'")
        await ctx.yield_output(result)


def build_basic_sequence_workflow() -> WorkflowBuilder:
    upper = UpperCaseExecutor(id="upper")
    reverse = ReverseTextExecutor(id="reverse")

    workflow = (
        WorkflowBuilder()        
        .set_start_executor(upper)
        .add_edge(upper, reverse)
        .build()
    )
    workflow.id = "01BSequence"
    return workflow
