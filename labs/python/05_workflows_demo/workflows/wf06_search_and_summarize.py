# workflows/wf06_search_and_summarize.py
import json
from agent_framework import (
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agents import AgentFactory
from logger import get_logger

logger = get_logger("maf.wf06_search_summarize")

# ------------------------------------------------------------
# Input node (user → ChatMessage)
# ------------------------------------------------------------
class InputToChat(Executor):
    @handler
    async def start(self, text: str, ctx: WorkflowContext[ChatMessage]):
        """Entry point for DevUI: takes plain text and emits ChatMessage."""
        logger.info(f"[InputToChat] user input: %s", text)
        await ctx.set_shared_state("user_query", text)
        await ctx.send_message(ChatMessage(role="user", text=text))

# ------------------------------------------------------------
# Search Executor (uses DuckDuckGo MCP)
# ------------------------------------------------------------
class SearchExecutor(Executor):
    """Performs the first research step: topic → list of relevant URLs."""

    def __init__(self, factory: AgentFactory, id="search_executor"):
        super().__init__(id=id)
        self.agent = factory.get("SearchAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[list[str]]):
        user_query = await ctx.get_shared_state("user_query")
        query_text = user_query or message.text
        logger.info("[SearchExecutor] Searching for: %s", query_text)

        # Make sure the query uses both context and message
        enriched_prompt = ChatMessage(
            role="user",
            text=f"Find the most relevant articles or sources for the question:\n'{query_text}'"
        )

        response = await self.agent.run([enriched_prompt])
        raw = (response.text or "").strip()

        urls = []
        try:
            urls = json.loads(raw)
            if not isinstance(urls, list):
                raise ValueError("Not a JSON list")
        except Exception as e:
            logger.warning("[SearchExecutor] JSON parsing failed: %s", e)
            import re
            urls = re.findall(r'https?://\S+', raw)

        urls = list(dict.fromkeys(urls))[:10]
        logger.info("[SearchExecutor] Extracted %d URLs", len(urls))

        await ctx.set_shared_state("search_results", urls)
        await ctx.send_message(urls)

# ------------------------------------------------------------
# Fetch Executor (fetches + summarizes content)
# ------------------------------------------------------------
class FetchExecutor(Executor):
    """Fetches content from multiple URLs and emits summarized text."""
    
    def __init__(self, factory: AgentFactory, id="fetch_agent"):
        super().__init__(id=id)
        self.agent = factory.get("FetchAgent")

    @handler
    async def handle(self, urls: list[str], ctx: WorkflowContext[ChatMessage]):
        
        user_query = await ctx.get_shared_state("user_query")
        if not urls:
            logger.warning("[FetchExecutor] No URLs provided.")
            await ctx.yield_output(ChatMessage(role="assistant", text="No URLs to fetch."))
            return

        logger.info("[FetchExecutor] Fetching %d URLs...", len(urls))
        urls_text = "\n".join(urls)
        prompt = ChatMessage(
            role="user",
            text=(
                f"You are performing research for the question:\n'{user_query}'.\n"
                "Fetch and summarize the following web pages. "
                "Focus on extracting information that helps answer the question. "
                "Separate each site summary with '---'.\n\n"
                f"{urls_text}"
            ),
        )

        response = await self.agent.run([prompt])
        fetched_text = (response.text or "").strip()
        await ctx.set_shared_state("fetched_summary", fetched_text)
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
            user_query = await ctx.get_shared_state("user_query")
            fetched_summary = await ctx.get_shared_state("fetched_summary") or message.text

            combined_prompt = ChatMessage(
                role="user",
                text=(
                    f"You are writing a concise research summary that directly answers this question:\n"
                    f"'{user_query}'.\n\n"
                    "Here is the collected material:\n\n"
                    f"{fetched_summary}\n\n"
                    "Write a clear, factual answer, focused strictly on the question."
                ),
            )

            response = await self.agent.run([combined_prompt])
            result = (response.text or "").strip()
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
    workflow.id = "06SearchAndSumm"
    return workflow
