from agent_framework import Executor, WorkflowContext, WorkflowBuilder, WorkflowOutputEvent, handler

# ------------------------------------------------------------
# Step 1. Transformation logic
# ------------------------------------------------------------
class TransformExecutor(Executor):
    @handler
    async def transform(self, text: str, ctx: WorkflowContext[str]) -> None:
        new_text = text + "!"
        print(f"[TransformExecutor] '{text}' -> '{new_text}'")
        await ctx.send_message(new_text)


# ------------------------------------------------------------
# Step 2. Judge if the condition is satisfied
# ------------------------------------------------------------
class JudgeExecutor(Executor):
    @handler
    async def evaluate(self, text: str, ctx: WorkflowContext[str]) -> None:
        if len(text) < 10:
            print(f"[JudgeExecutor] '{text}' too short → loop again")
            # send message back to Transform (loop)
            await ctx.send_message(("continue", text))
        else:
            print(f"[JudgeExecutor] '{text}' long enough → end")
            await ctx.send_message(("done", text))


# ------------------------------------------------------------
# Step 3. Output result
# ------------------------------------------------------------
class OutputExecutor(Executor):
    @handler
    async def finish(self, text: str, ctx: WorkflowContext[str]) -> None:
        print(f"[OutputExecutor] Final result: '{text}'")
        await ctx.yield_output(text)


# ------------------------------------------------------------
# Workflow definition
# ------------------------------------------------------------
def build_loop_with_evaluation_workflow() -> WorkflowBuilder:
    transform = TransformExecutor(id="transform")
    judge = JudgeExecutor(id="judge")
    output = OutputExecutor(id="output")

    workflow = (
        WorkflowBuilder()
        .set_start_executor(transform)
        # Main loop edges
        .add_edge(transform, judge)
        # Conditional edges based on tuple[0] value
        .add_edge(judge, transform, condition=lambda signal: signal[0] == "continue")
        .add_edge(judge, output, condition=lambda signal: signal[0] == "done")
        .build()
    )

    workflow.id = "LoopWithEvaluation"
    return workflow
