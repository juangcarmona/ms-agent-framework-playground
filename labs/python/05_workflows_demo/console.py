# console.py
"""
Console runner for Microsoft Agent Framework workflows.
Used when DevUI cannot render HITL or interactive checkpoints.

Usage:
  python console.py --wf SearchWithCheckpoint
  python console.py --wf SearchWithCheckpoint --resume <checkpoint_id>
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from agent_framework import (
    WorkflowOutputEvent,
    RequestInfoEvent,
    WorkflowStatusEvent,
    WorkflowRunState,
)
from config import MCP_GATEWAY_URL

from agents import AgentFactory
from persistence.checkpoint_storage_factory import CheckpointStorageFactory
from tools import mcp_tools
from tools.mcp_gateway_client import MCPGatewayClient
from workflows.workflow_factory import WorkflowFactory

# ------------------------------------------------------------------------------
# Logging setup
# ------------------------------------------------------------------------------

class ConsoleFormatter(logging.Formatter):
    """Pretty, colorized console logs."""

    COLORS = {
        "DEBUG": "\033[90m",    # grey
        "INFO": "\033[94m",     # blue
        "WARNING": "\033[93m",  # yellow
        "ERROR": "\033[91m",    # red
        "CRITICAL": "\033[95m", # magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        name = record.name.replace("maf.", "")
        msg = record.getMessage()
        return f"{color}{ts} [{record.levelname:<8}] {name}: {msg}{self.RESET}"

# --- Handlers ---
stream_handler = logging.StreamHandler(sys.stdout)   # terminal output
stream_handler.setFormatter(ConsoleFormatter())

debug_handler = logging.StreamHandler(sys.stderr)    # VSCode debug console
debug_handler.setFormatter(ConsoleFormatter())

root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers.clear()
# root.addHandler(stream_handler)
root.addHandler(debug_handler)

# quiet down noisy libs
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("anyio").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("maf.console")



# ------------------------------------------------------------------------------
# Utility: Collect workflow events and handle HITL interactions
# ------------------------------------------------------------------------------

async def consume_events(stream):
    """Collect and log events nicely."""
    events = []
    async for event in stream:
        events.append(event)
        logger.debug(f"Event received: {event.__class__.__name__}")
    return events


async def prompt_for_responses(requests):
    """Ask the human for responses (via stdin)."""
    responses = {}
    for ev in requests:
        req = ev.data
        logger.warning("=== Human input required ===")
        logger.warning(f"Prompt: {req.prompt}")
        answer = input("🧠 Your answer: ").strip()
        responses[ev.request_id] = answer
    return responses


async def run_interactive(workflow, initial_input: str = "Start workflow"):
    """Run workflow interactively, handling HITL loops."""
    events = await consume_events(workflow.run_stream(initial_input))

    while True:
        pending = [e for e in events if isinstance(e, RequestInfoEvent)]

        for ev in events:
            if isinstance(ev, WorkflowOutputEvent):
                logger.info("✅ Workflow completed with output:")
                logger.info(str(ev.data))
                return

        if not pending:
            for ev in events:
                if isinstance(ev, WorkflowStatusEvent) and ev.state == WorkflowRunState.IDLE:
                    logger.info("(No pending HITL requests — workflow idle.)")
                    return
            await asyncio.sleep(0.5)
            continue

        responses = await prompt_for_responses(pending)
        events = await consume_events(workflow.send_responses_streaming(responses))


async def resume_from_checkpoint(workflow, checkpoint_storage, checkpoint_id: str):
    logger.info(f"⏩ Resuming from checkpoint: {checkpoint_id}")
    events = await consume_events(
        workflow.run_stream_from_checkpoint(
            checkpoint_id,
            checkpoint_storage=checkpoint_storage,
        )
    )
    pending = [e for e in events if isinstance(e, RequestInfoEvent)]
    if pending:
        responses = await prompt_for_responses(pending)
        await consume_events(workflow.send_responses_streaming(responses))


# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------

async def main():
    parser = argparse.ArgumentParser(description="Run a workflow in console mode (with HITL support).")
    parser.add_argument("--wf", required=True, help="Workflow ID to run (e.g., SearchWithCheckpoint)")
    parser.add_argument("--resume", help="Optional checkpoint ID to resume from")
    parser.add_argument("--input", help="Optional initial user input text", default="Research Docker MCP Gateway")
    args = parser.parse_args()

    # 1️⃣ Initialize MCP + Agents
    mcp_client = MCPGatewayClient(MCP_GATEWAY_URL)
    await mcp_client.connect()
    await mcp_client.list_tools()
    mcp_tools.init_mcp_client(mcp_client)

    # Init
    agent_factory = AgentFactory().init_defaults()
    storage_factory = CheckpointStorageFactory()
    checkpoint_storage = await storage_factory.init_postgres()

    wf_factory = WorkflowFactory(agent_factory, checkpoint_storage).init_defaults()

    # Pick workflow by ID
    workflow = wf_factory.get(args.wf)

    # 4️⃣ Run or resume
    if args.resume:
        await resume_from_checkpoint(workflow, checkpoint_storage, args.resume)
    else:
        await run_interactive(workflow, args.input)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
