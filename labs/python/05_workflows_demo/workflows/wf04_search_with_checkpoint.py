from email.mime import message
import logging
from dataclasses import dataclass
from agent_framework import (
    ChatMessage,
    Executor,
    RequestInfoExecutor,
    RequestInfoMessage,
    RequestResponse,
    Role,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agents import AgentFactory

logger = logging.getLogger("maf.wf04")


# ---------- 1) Base executors ----------

class InputToChat(Executor):
    @handler
    async def start(self, text: str, ctx: WorkflowContext[ChatMessage]):
        logger.info("[InputToChat] user input: %s", text)
        await ctx.send_message(ChatMessage(role="user", text=text))


class SearchExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="search_agent"):
        super().__init__(id=id)
        self.agent = factory.get("SearchAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        response = await self.agent.run([message])
        await ctx.send_message(ChatMessage(role="assistant", text=(response.text or "").strip()))


class FetchExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="fetch_agent"):
        super().__init__(id=id)
        self.agent = factory.get("FetchAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        response = await self.agent.run([message])
        text = (response.text or "").strip()
        logger.info("[FetchExecutor] fetched %d chars", len(text))
        # persist for checkpoints
        await ctx.set_state({"last_fetch_len": len(text)})
        await ctx.set_shared_state("fetched_text", text) 
        await ctx.send_message(ChatMessage(role="assistant", text=text))


# ---------- 2) HITL via ApprovalGateway (RequestInfoExecutor) ----------

@dataclass
class HumanApprovalRequest(RequestInfoMessage):
    """Custom HITL request that includes a prompt and a preview."""
    prompt: str = ""
    preview: str = ""
    iteration: int = 1


class ApprovalGateway(Executor):
    def __init__(self, reviewer_id: str, next_id: str, id="approval_gateway"):
        super().__init__(id=id)
        self._reviewer_id = reviewer_id
        self._next_id = next_id

    @handler
    async def ask_human(self, message: ChatMessage, ctx: WorkflowContext[HumanApprovalRequest]):
        shared = await ctx.get_shared_state() or {}  
        preview = (shared.get("fetched_text") or message.text or "")[:400]
        await ctx.set_state({"last_preview_len": len(preview)})

        req = HumanApprovalRequest(
            prompt="Do you want to create a full Markdown report? Reply 'yes' or 'no'.",
            preview=preview,
        )
        await ctx.send_message(req, target_id=self._reviewer_id)

    @handler
    async def on_human_feedback(
        self,
        feedback: RequestResponse[HumanApprovalRequest, str],
        ctx: WorkflowContext[ChatMessage],
    ):
        reply = (feedback.data or "").strip().lower()
        logger.info("[ApprovalGateway] Human replied: %s", reply)

        if reply == "yes":
            # Forward to summarizer
            await ctx.send_message(ChatMessage(role="user", text="Proceed with full report"), target_id=self._next_id)
        else:
            await ctx.yield_output("Human declined to continue.")


# ---------- 3) Summarizer ----------

class SummarizerExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="summarizer_agent"):
        super().__init__(id=id)
        self.agent = factory.get("SummarizerAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[str]):
        shared = await ctx.get_shared_state() or {}
        fetched_text = shared.get("fetched_text", "")
        if fetched_text:
            # Combine the human approval message with fetched content
            combined = f"{message.text}\n\n---\n{fetched_text}"
        else:
            combined = message.text

        response = await self.agent.run([ChatMessage(role="user", text=combined)])
        result = (response.text or "").strip()
        await ctx.yield_output(result)
        logger.info("[Summarizer] produced %d chars", len(result))


# ---------- 4) Workflow builder ----------

def build_search_with_checkpoint_workflow(factory: AgentFactory, checkpoint_storage):
    entry = InputToChat(id="input_to_chat")

    # Agentic executors
    searcher = SearchExecutor(factory=factory)
    fetcher = FetchExecutor(factory=factory)
    summarizer = SummarizerExecutor(factory=factory)
    
    # We could have mutliple approval gateways for different steps
    review = RequestInfoExecutor(id="request_info")
    approval = ApprovalGateway(reviewer_id=review.id, next_id=summarizer.id) 

    builder = (
        WorkflowBuilder()
        .set_start_executor(entry)
        .add_edge(entry, searcher)
        .add_edge(searcher, fetcher)
        .add_edge(fetcher, approval)      # AI → ApprovalGateway (ask human)
        .add_edge(approval, review)       # ApprovalGateway → RequestInfoExecutor
        .add_edge(review, approval)       # human response goes back to ApprovalGateway
        .add_edge(approval, summarizer)   # ApprovalGateway sends final approval downstream
        .with_checkpointing(checkpoint_storage)
    )

    wf = builder.build()
    wf.id = "SearchWithCheckpoint"
    return wf
