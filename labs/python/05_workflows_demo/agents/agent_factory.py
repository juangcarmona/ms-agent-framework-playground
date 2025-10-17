# agents/agent_factory.py
from agent_framework.openai import OpenAIChatClient
from .general_agent import build_general_agent
from .summarizer_agent import build_summarizer_agent
from .search_agent import build_search_agent
from .fetch_agent import build_fetch_agent
from .title_generator_agent import build_title_generator_agent

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
