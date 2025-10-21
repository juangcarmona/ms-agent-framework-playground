import logging
from typing import Dict

from agent_framework import Workflow
from agents import AgentFactory

from logger import get_logger
from persistence.checkpoint_storage_factory import CheckpointStorageFactory

# Import builders
from .wf01_basic_sequence import build_basic_sequence_workflow
from .wf02_sequential_executors import build_sequential_executors_workflow
from .wf03_conditional_branch import build_conditional_branching_workflow
from .wf04_parallel_fanout import build_parallel_fanout_workflow
from .wf05_loop_with_evaluation import build_loop_with_evaluation_workflow
from .wf06_search_and_summarize import build_search_and_summarize_workflow
from .wf07_search_with_hitl import build_search_with_hitl_workflow
from .wf08_search_with_multiagent_and_tooling import build_search_with_multiagent_and_tooling_workflow

logger = get_logger("maf.workflow_factory")


class WorkflowFactory:
    """
    Central registry and factory for all Workflows.
    Each workflow is registered using its own `workflow.id` value
    (as defined inside the builder).
    """

    def __init__(self, agent_factory: AgentFactory, checkpoint_storage: CheckpointStorageFactory):
        self._agent_factory = agent_factory
        self._checkpoint_storage = checkpoint_storage
        self._registry: Dict[str, Workflow] = {}

    # -------------------------------------------------------
    # Initialization
    # -------------------------------------------------------
    def init_defaults(self):
        """
        Instantiate all default workflows and register them by their internal ID.
        """
        builder_fns = [
            lambda: build_basic_sequence_workflow(),
            lambda: build_sequential_executors_workflow(self._agent_factory),
            lambda: build_conditional_branching_workflow(),
            lambda: build_parallel_fanout_workflow(),
            lambda: build_loop_with_evaluation_workflow(),
            lambda: build_search_and_summarize_workflow(self._agent_factory),
            lambda: build_search_with_hitl_workflow(self._agent_factory, self._checkpoint_storage),
            lambda: build_search_with_multiagent_and_tooling_workflow(self._agent_factory, self._checkpoint_storage),
        ]

        for build_fn in builder_fns:
            try:
                wf = build_fn()
                wf_id = getattr(wf, "id", None)
                if not wf_id:
                    raise ValueError("Workflow builder did not set `workflow.id`")
                self._registry[wf_id] = wf
                logger.info(f"✅ Registered workflow: {wf_id}")
            except Exception as e:
                logger.error(f"❌ Failed to build workflow: {e}")

        return self

    # -------------------------------------------------------
    # Access methods
    # -------------------------------------------------------
    def get(self, wf_id: str) -> Workflow:
        if wf_id not in self._registry:
            raise KeyError(f"Workflow '{wf_id}' not found. Available: {list(self._registry)}")
        return self._registry[wf_id]

    def all(self):
        return list(self._registry.values())
