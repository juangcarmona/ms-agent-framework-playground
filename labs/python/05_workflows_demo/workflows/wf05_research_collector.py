import logging
from agent_framework import (
    ChatMessage,
    Executor,
    WorkflowBuilder,
    WorkflowContext,
    handler,
)
from agents import AgentFactory

logger = logging.getLogger("maf.wf05")


# ------------------------------------------------------------
# 1️⃣ Input node
# ------------------------------------------------------------
class InputToChat(Executor):
    @handler
    async def start(self, text: str, ctx: WorkflowContext[ChatMessage]):
        logger.info("[InputToChat] user input: %s", text)
        await ctx.set_shared_state("user_query", text)
        await ctx.send_message(ChatMessage(role="user", text=text))


# ------------------------------------------------------------
# 2️⃣ Title generation
# ------------------------------------------------------------
class TitleGeneratorExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="title_generator"):
        super().__init__(id=id)
        self.agent = factory.get("TitleGeneratorAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        user_query = await ctx.get_shared_state("user_query")
        response = await self.agent.run([ChatMessage(role="user", text=user_query)])
        title = (response.text or "untitled").strip()
        await ctx.set_shared_state("research_title", title)
        logger.info("[TitleGenerator] Generated title: %s", title)
        await ctx.send_message(ChatMessage(role="assistant", text=title))


# ------------------------------------------------------------
# 3️⃣ Folder creation
# ------------------------------------------------------------
class FolderCreatorExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="folder_creator"):
        super().__init__(id=id)
        self.agent = factory.get("FolderManagerAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        title = await ctx.get_shared_state("research_title")
        response = await self.agent.run([
            ChatMessage(role="user", text=f"Create a folder for: {title}")
        ])
        folder_path = response.text.strip()
        await ctx.set_shared_state("folder_path", folder_path)
        logger.info("[FolderCreator] Folder created at: %s", folder_path)
        await ctx.send_message(ChatMessage(role="assistant", text=folder_path))


# ------------------------------------------------------------
# 4️⃣ Search (DuckDuckGo MCP)
# ------------------------------------------------------------
class SearchExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="search_agent"):
        super().__init__(id=id)
        self.agent = factory.get("SearchAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        title = await ctx.get_shared_state("research_title")
        response = await self.agent.run([
            ChatMessage(role="user", text=f"Search for the topic: {title}")
        ])
        urls = [u for u in (response.text or "").split() if u.startswith("http")]
        await ctx.set_shared_state("search_results", urls[:10])
        logger.info("[SearchExecutor] Found %d URLs", len(urls[:10]))
        await ctx.send_message(ChatMessage(role="assistant", text=f"Found {len(urls[:10])} URLs."))


# ------------------------------------------------------------
# 5️⃣ Collect, summarize, and save results
# ------------------------------------------------------------
class CollectorExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="collector_agent"):
        super().__init__(id=id)
        self.agent = factory.get("CollectorAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[ChatMessage]):
        urls = await ctx.get_shared_state("search_results") or []
        folder = await ctx.get_shared_state("folder_path")
        if not urls:
            logger.warning("[Collector] No URLs found, skipping.")
            return

        prompt = (
            f"Store Markdown summaries for these URLs into folder:\n{folder}\n\n"
            f"URLs:\n" + "\n".join(urls) +
            "\nEach summary must include a # TL;DR section."
        )
        response = await self.agent.run([ChatMessage(role="user", text=prompt)])
        summary_index = (response.text or "").strip()
        await ctx.set_shared_state("summary_index", summary_index)
        logger.info("[Collector] Finished processing all URLs.")
        await ctx.send_message(ChatMessage(role="assistant", text="All pages processed and saved."))


# ------------------------------------------------------------
# 6️⃣ Folder synthesis
# ------------------------------------------------------------
class FolderSummarizerExecutor(Executor):
    def __init__(self, factory: AgentFactory, id="research_aggregator"):
        super().__init__(id=id)
        self.agent = factory.get("ResearchAggregatorAgent")

    @handler
    async def handle(self, message: ChatMessage, ctx: WorkflowContext[str]):
        folder = await ctx.get_shared_state("folder_path")
        prompt = (
            f"Read all Markdown files from folder:\n{folder}\n"
            "Extract the '# TL;DR' sections and produce a unified research summary."
        )
        response = await self.agent.run([ChatMessage(role="user", text=prompt)])
        result = (response.text or "").strip()
        await ctx.set_shared_state("final_summary", result)
        await ctx.yield_output(result)
        logger.info("[FolderSummarizer] Global synthesis produced (%d chars)", len(result))


# ------------------------------------------------------------
# 7️⃣ Workflow definition
# ------------------------------------------------------------
def build_research_collector_workflow(factory: AgentFactory, checkpoint_storage):
    entry = InputToChat(id="input_to_chat")
    title = TitleGeneratorExecutor(factory=factory)
    folder = FolderCreatorExecutor(factory=factory)
    searcher = SearchExecutor(factory=factory)
    collector = CollectorExecutor(factory=factory)
    summarizer = FolderSummarizerExecutor(factory=factory)

    builder = (
        WorkflowBuilder()
        .set_start_executor(entry)
        .add_edge(entry, title)
        .add_edge(title, folder)
        .add_edge(folder, searcher)
        .add_edge(searcher, collector)
        .add_edge(collector, summarizer)
        .with_checkpointing(checkpoint_storage)
    )

    wf = builder.build()
    wf.id = "ResearchCollector"
    return wf
