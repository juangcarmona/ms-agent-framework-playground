# workflows/workflow_factory.py
import logging
from typing import Dict

from agent_framework import Workflow
from agents import AgentFactory
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
            "ConditionalBranching": lambda: build_conditional_branching_workflow(),
            "ParallelFanOut": lambda: build_parallel_fanout_workflow(),
            "LoopWithEvaluation": lambda: build_loop_with_evaluation_workflow(),
            "SearchAndSummarize": lambda: build_search_and_summarize_workflow(self._agent_factory),
            "SearchWithHitL": lambda: build_search_with_hitl_workflow(self._agent_factory, self._checkpoint_storage),
            "SearchWithMultiAgentAndTooling": lambda: build_search_with_multiagent_and_tooling_workflow(self._agent_factory, self._checkpoint_storage),      
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
