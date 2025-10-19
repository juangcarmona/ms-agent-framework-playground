# agents/agent_factory.py
from agent_framework.openai import OpenAIChatClient
from .general_agent import build_general_agent
from .summarizer_agent import build_summarizer_agent
from .search_agent import build_search_agent
from .fetch_agent import build_fetch_agent
from .title_generator_agent import build_title_generator_agent
from .pure_fetch_agent import build_pure_fetch_agent
from .markdown_summarizer_agent import build_markdown_summarizer_agent
from .research_aggregator_agent import build_research_aggregator_agent
from .folder_manager_agent import build_folder_manager_agent
from .collector_agent import build_collector_agent
from .sys_exec_agent import build_sys_exec_agent
from .file_organizer_agent import build_file_organizer_agent
from .system_inspector_agent import build_system_inspector_agent
from .dev_helper_agent import build_dev_helper_agent

from config import OPENAI_API_BASE, OPENAI_API_KEY, MODEL_ID


class AgentFactory:
    """
    Central registry and factory for all ChatAgents.
    Keeps model configuration consistent and allows discovery by name.
    """

    def __init__(self):
        self._client = OpenAIChatClient(
            base_url=OPENAI_API_BASE,
            api_key=OPENAI_API_KEY,
            model_id=MODEL_ID,
        )
        self._registry: dict[str, object] = {}

    # -------------------------------------------------------
    # Initialization
    # -------------------------------------------------------
    def init_defaults(self):
        builders = {
            "GeneralAgent": build_general_agent,
            "SummarizerAgent": build_summarizer_agent,
            "SearchAgent": build_search_agent,
            "FetchAgent": build_fetch_agent,
            "TitleGeneratorAgent": build_title_generator_agent,
            "PureFetcherAgent": build_pure_fetch_agent,
            "MarkdownSummarizerAgent": build_markdown_summarizer_agent,
            "ResearchAggregatorAgent": build_research_aggregator_agent,   
            "FolderManagerAgent": build_folder_manager_agent,
            "CollectorAgent": build_collector_agent,
            "SysExecAgent": build_sys_exec_agent,
            "FileOrganizerAgent": build_file_organizer_agent,
            "SystemInspectorAgent": build_system_inspector_agent,
            "DevHelperAgent": build_dev_helper_agent,
        }
        for name, builder in builders.items():
            agent = builder(self._client)
            self._registry[name] = agent
        return self

    # -------------------------------------------------------
    # Access methods
    # -------------------------------------------------------
    def get(self, name: str):
        try:
            return self._registry[name]
        except KeyError:
            raise KeyError(f"Agent '{name}' not registered in factory. Available: {list(self._registry)}")

    def all(self):
        return list(self._registry.values())
