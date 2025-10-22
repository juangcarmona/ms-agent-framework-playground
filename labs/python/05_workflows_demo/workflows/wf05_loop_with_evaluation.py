# workflows/wf05_loop_with_evaluation.py
import asyncio
from agent_framework import Executor, WorkflowContext, WorkflowBuilder, handler
from logger import get_logger

logger = get_logger("maf.wf05")

class LoopDispatcher(Executor):
    @handler
    async def dispatch(self, text: str, ctx: WorkflowContext[str]) -> None:
        logger.info(f"Dispatching '{text}' to loop...")
        await ctx.send_message(text)

class TransformExecutor(Executor):
    @handler
    async def transform(self, data: str, ctx: WorkflowContext[str]) -> None:
        new_text = data + "!"
        logger.info(f"[TransformExecutor] '{data}' -> '{new_text}'")
        # Let's wait a bit to simulate processing time
        await asyncio.sleep(0.2)
        await ctx.send_message(new_text)


class JudgeExecutor(Executor):
    @handler
    async def evaluate(self, text: str, ctx: WorkflowContext[str | dict]) -> None:
        if len(text) < 10:
            logger.info(f"'{text}' too short → loop again")
            await ctx.send_message(text)  # str
        else:
            logger.info(f"'{text}' long enough → end")
            await ctx.send_message({"action": "done", "text": text})  # dict


class OutputExecutor(Executor):
    @handler
    async def finish(self, data: str | dict, ctx: WorkflowContext[str]) -> None:
        if isinstance(data, dict):
            logger.info(f"Final result: '{data['text']}'")
            await ctx.yield_output(data["text"])
        else:
            # Shouldn't happen under normal conditions
            logger.warning(f"Unexpected non-dict input: {data}")
            await ctx.yield_output(data)


def build_loop_with_evaluation_workflow() -> WorkflowBuilder:
    dispatcher = LoopDispatcher(id="dispatcher")
    transform = TransformExecutor(id="transform")
    judge = JudgeExecutor(id="judge")
    output = OutputExecutor(id="output")

    wf = (
        WorkflowBuilder()
        .set_start_executor(dispatcher)
        .add_edge(dispatcher, transform)
        .add_edge(transform, judge)
        .add_edge(judge, transform, condition=lambda d: isinstance(d, str))
        .add_edge(judge, output, condition=lambda d: isinstance(d, dict) and d.get("action") == "done")
        .build()
    )

    wf.id = "05LoopEval"
    return wf
