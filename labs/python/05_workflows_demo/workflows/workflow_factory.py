# workflows/workflow_factory.py
import logging
from typing import Dict

from agent_framework import Workflow
from agents import AgentFactory
from persistence.checkpoint_storage_factory import CheckpointStorageFactory

# Import builders
from .wf01_basic_sequence import build_basic_sequence_workflow
from .wf02_sequential_executors import build_sequential_executors_workflow
from .wf03_search_and_summarize import build_search_and_summarize_workflow
from .wf04_search_with_checkpoint import build_search_with_checkpoint_workflow

logger = logging.getLogger("maf.workflow_factory")


class WorkflowFactory:
    """
    Central registry and factory for all Workflows.
    Provides consistent initialization and allows retrieval by ID.
    """

    def __init__(self, agent_factory: AgentFactory, checkpoint_storage: CheckpointStorageFactory):
        self._agent_factory = agent_factory
        self._checkpoint_storage = checkpoint_storage
        self._registry: Dict[str, Workflow] = {}

    # -------------------------------------------------------
    # Initialization
    # -------------------------------------------------------
    def init_defaults(self):
        builders = {
            "BasicSequence": lambda: build_basic_sequence_workflow(),
            "SequentialExecutors": lambda: build_sequential_executors_workflow(self._agent_factory),
            "SearchAndSummarize": lambda: build_search_and_summarize_workflow(self._agent_factory),
            "SearchWithCheckpoint": lambda: build_search_with_checkpoint_workflow(
                self._agent_factory, self._checkpoint_storage
            ),
        }

        for name, builder in builders.items():
            try:
                wf = builder()
                wf.id = name
                self._registry[name] = wf
                logger.info(f"✅ Registered workflow: {name}")
            except Exception as e:
                logger.error(f"❌ Failed to build workflow {name}: {e}")

        return self

    # -------------------------------------------------------
    # Access methods
    # -------------------------------------------------------
    def get(self, wf_id: str):
        try:
            return self._registry[wf_id]
        except KeyError:
            raise KeyError(f"Workflow '{wf_id}' not found. Available: {list(self._registry)}")

    def all(self):
        return list(self._registry.values())
