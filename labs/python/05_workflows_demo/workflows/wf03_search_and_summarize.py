import logging
from agent_framework import (
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agents import AgentFactory

logger = logging.getLogger("maf.wf03")

# ------------------------------------------------------------
# Input node (user → ChatMessage)
# ------------------------------------------------------------
class InputToChat(Executor):
    @handler
    async def start(self, text: str, ctx: WorkflowContext[ChatMessage]):
        """Entry point for DevUI: takes plain text and emits ChatMessage."""
        logger.info(f"[InputToChat] user input: %s", text)
        await ctx.send_message(ChatMessage(role="user", text=text))

# ------------------------------------------------------------
# Search Executor (uses DuckDuckGo MCP)
# ------------------------------------------------------------
class SearchExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="search_agent"):
        super().__init__(id=id)
        self.agent = factory.get("SearchAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        """Runs the search and emits a single assistant message with URLs."""
        response = await self.agent.run([message])
        urls_text = (response.text or "").strip()
        logger.info("[SearchExecutor] Retrieved %d chars", len(urls_text))
        logger.debug("Search results:\n%s", urls_text)
        await ctx.send_message(ChatMessage(role="assistant", text=urls_text))

# ------------------------------------------------------------
# Fetch Executor (fetches + summarizes content)
# ------------------------------------------------------------
class FetchExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="fetch_agent"):
        super().__init__(id=id)
        self.agent = factory.get("FetchAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        """Fetches content from given URLs and emits summarized text."""
        response = await self.agent.run([message])
        fetched_text = (response.text or "").strip()
        snippet = fetched_text[:120].replace("\n", " ")
        logger.info("[FetchExecutor] Fetched summary (%d chars)", len(fetched_text))
        logger.debug("[FetchExecutor] Preview: %s...", snippet)
        if not fetched_text:
            logger.warning("[FetchExecutor] No fetched text returned.")
        await ctx.send_message(ChatMessage(role="assistant", text=fetched_text))

# ------------------------------------------------------------
# Summarizer Executor (final synthesis)
# ------------------------------------------------------------
class SummarizerExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="summarizer_agent"):
        super().__init__(id=id)
        self.agent = factory.get("SummarizerAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[str]):
        """Synthesizes the final output based on fetched summaries."""
        try:
            response = await self.agent.run([message])
            result = (response.text or "").strip()
            logger.info("[SummarizerExecutor] Final answer produced (%d chars)", len(result))
            await ctx.yield_output(result)
        except Exception as e:
            logger.exception("[SummarizerExecutor] Error during summarization: %s", e)
            await ctx.yield_output("⚠️ Summarizer failed.")

# ------------------------------------------------------------
# Workflow definition
# ------------------------------------------------------------
def build_search_and_summarize_workflow(factory: AgentFactory):
    entry = InputToChat(id="input_to_chat")
    searcher = SearchExecutor(factory=factory)
    fetcher = FetchExecutor(factory=factory)
    summarizer = SummarizerExecutor(factory=factory)

    workflow = (
        WorkflowBuilder()
        .set_start_executor(entry)
        .add_edge(entry, searcher)
        .add_edge(searcher, fetcher)
        .add_edge(fetcher, summarizer)
        .build()
    )
    return workflow
