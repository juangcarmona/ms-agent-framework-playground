from agent_framework import (
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agents import AgentFactory

# ------------------------------------------------------------
# Entry node: plain text → ChatMessage
# ------------------------------------------------------------
class InputToChat(Executor):
    @handler
    async def start(self, text: str, ctx: WorkflowContext[ChatMessage]):
        print(f"[InputToChat] user input: {text}")
        await ctx.send_message(ChatMessage(role="user", text=text))

# ------------------------------------------------------------
# Agent wrappers (use existing ChatAgents from AgentFactory)
# ------------------------------------------------------------
class GeneralExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="general_agent"):
        super().__init__(id=id)
        self.agent = factory.get("GeneralAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        response = await self.agent.run([message])
        await ctx.send_message(response.messages[-1])

class SummarizerExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="summarizer"):
        super().__init__(id=id)
        self.agent = factory.get("SummarizerAgent")

    @handler
    async def handle(self, messages: ChatMessage, ctx: WorkflowContext[str]):
        response = await self.agent.run([messages])
        await ctx.yield_output(response.text)

# ------------------------------------------------------------
# Workflow definition
# ------------------------------------------------------------
def build_sequential_executors_workflow(factory: AgentFactory):
    entry = InputToChat(id="input_to_chat")

    general = GeneralExecutor(factory=factory, id="general_agent")
    summarizer = SummarizerExecutor(factory=factory, id="summarizer")

    workflow = (
        WorkflowBuilder()
        .set_start_executor(entry)
        .add_edge(entry, general)
        .add_edge(general, summarizer)
        .build()
    )
    workflow.id = "SequentialExecutors"
    return workflow
