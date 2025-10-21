import re
from agent_framework import Executor, WorkflowBuilder, WorkflowContext, WorkflowOutputEvent, handler

# ------------------------------------------------------------
# Step 1 — Input normalization
# ------------------------------------------------------------
class NormalizeInput(Executor):
    @handler
    async def normalize(self, text: str, ctx: WorkflowContext[str]) -> None:
        normalized = text.strip().lower()
        print(f"[NormalizeInput] '{text}' → '{normalized}'")
        await ctx.send_message(normalized)


# ------------------------------------------------------------
# Step 2 — Intent classification
# ------------------------------------------------------------
class IntentClassifier(Executor):
    """
    Simple content-based routing using keywords.
    Detects intents: support, sales, or hr.
    """
    @handler
    async def classify(self, text: str, ctx: WorkflowContext[dict]) -> None:
        # NOTE: In real scenarios, use an NLP model for intent classification
        # Or, working with agents, call an intent classification agent here.
        intent = None
        if re.search(r"(error|issue|problem|bug)", text):
            intent = "support"
        elif re.search(r"(buy|price|quote|discount)", text):
            intent = "sales"
        elif re.search(r"(job|hiring|career|salary|hire)", text):
            intent = "hr"
        else:
            intent = "unknown"

        print(f"[IntentClassifier] Intent detected: {intent}")
        await ctx.send_message({"intent": intent, "content": text})


# ------------------------------------------------------------
# Step 3a — Support handler
# ------------------------------------------------------------
class SupportExecutor(Executor):
    @handler
    async def handle(self, data: dict, ctx: WorkflowContext[str]) -> None:
        msg = f"🛠 Support: '{data['content']}'"
        print(msg)
        await ctx.yield_output(msg)


# ------------------------------------------------------------
# Step 3b — Sales handler
# ------------------------------------------------------------
class SalesExecutor(Executor):
    @handler
    async def handle(self, data: dict, ctx: WorkflowContext[str]) -> None:
        msg = f"💰 Sales: '{data['content']}'"
        print(msg)
        await ctx.yield_output(msg)


# ------------------------------------------------------------
# Step 3c — HR handler
# ------------------------------------------------------------
class HRExecutor(Executor):
    @handler
    async def handle(self, data: dict, ctx: WorkflowContext[str]) -> None:
        msg = f"👩‍💼 HR: '{data['content']}'"
        print(msg)
        await ctx.yield_output(msg)


# ------------------------------------------------------------
# Step 3d — Fallback handler
# ------------------------------------------------------------
class FallbackExecutor(Executor):
    @handler
    async def handle(self, data: dict, ctx: WorkflowContext[str]) -> None:
        msg = f"🤷 Unknown intent: '{data['content']}'"
        + "You might use an intent classification agent here"
        print(msg)
        await ctx.yield_output(msg)


# ------------------------------------------------------------
# Selection function (dynamic routing)
# ------------------------------------------------------------
def select_targets(data: dict, *args, **kwargs):
    intent = data.get("intent")
    targets = []
    if intent == "support":
        targets.append("support_exec")
    elif intent == "sales":
        targets.append("sales_exec")
    elif intent == "hr":
        targets.append("hr_exec")
    else:
        targets.append("fallback_exec")
    return targets


# ------------------------------------------------------------
# Workflow builder
# ------------------------------------------------------------
def build_conditional_branching_workflow() -> WorkflowBuilder:
    normalize = NormalizeInput(id="normalize")
    classifier = IntentClassifier(id="classifier")
    support = SupportExecutor(id="support_exec")
    sales = SalesExecutor(id="sales_exec")
    hr = HRExecutor(id="hr_exec")
    fallback = FallbackExecutor(id="fallback_exec")

    workflow = (
        WorkflowBuilder()
        .set_start_executor(normalize)
        .add_edge(normalize, classifier)
        .add_multi_selection_edge_group(
            classifier,
            [support, sales, hr, fallback],
            selection_func=select_targets,
        )
        .build()
    )

    workflow.id = "ConditionalBranching"
    return workflow
