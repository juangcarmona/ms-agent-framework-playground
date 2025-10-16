"""
Custom patch for Agent Framework DevUI to support STDIO MCP streaming.
Adds JSON-safe serialization for TextContent, FunctionCallContent, etc.

This also didn't work! See `non_working_1.py` and `non_working_2.py` for the original.
"""

import json, logging
from agent_framework_devui._server import DevServer
from agent_framework import _types as aft

logger = logging.getLogger(__name__)


class DevUIPatch:
    @staticmethod
    def safe_json(obj):
        """Recursively convert agent_framework content objects into JSON-serializable forms."""
        # Content primitives
        if isinstance(obj, (aft.TextContent, aft.TextReasoningContent)):
            return {"type": "text", "text": getattr(obj, "text", str(obj))}
        if isinstance(obj, aft.FunctionCallContent):
            return {
                "type": "function_call",
                "name": getattr(obj, "name", ""),
                "arguments": DevUIPatch.safe_json(getattr(obj, "arguments", {})),
                "call_id": getattr(obj, "call_id", ""),
            }
        if isinstance(obj, aft.FunctionResultContent):
            return {
                "type": "function_result",
                "call_id": getattr(obj, "call_id", ""),
                "result": DevUIPatch.safe_json(getattr(obj, "result", None)),
                "exception": getattr(obj, "exception", None),
            }
        if isinstance(obj, aft.DataContent):
            return {"type": "data", "data": DevUIPatch.safe_json(getattr(obj, "data", None))}
        if isinstance(obj, aft.ErrorContent):
            return {"type": "error", "message": getattr(obj, "message", str(obj))}
        if isinstance(obj, aft.UsageContent):
            try:
                return obj.to_dict(exclude={"raw_representation"}, exclude_none=True)
            except Exception:
                return {"type": "usage", "raw": str(obj)}

        # Containers
        if isinstance(obj, dict):
            return {k: DevUIPatch.safe_json(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            return [DevUIPatch.safe_json(v) for v in obj]

        # Pydantic models
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except Exception:
                pass

        # Primitive or fallback
        if isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        return str(obj)

    @staticmethod
    async def stream_execution(self, executor, request):
        """Replacement for DevServer._stream_execution with safe serialization."""
        try:
            async for event in executor.execute_streaming(request):
                try:
                    payload = json.dumps(
                        DevUIPatch.safe_json(event), ensure_ascii=False
                    )
                except Exception as e:
                    payload = json.dumps({"type": "error", "message": f"serialization failed: {e}"})
                yield f"data: {payload}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in patched streaming execution: {e}")
            err_payload = {
                "id": "error",
                "object": "error",
                "error": {"message": str(e), "type": "execution_error"},
            }
            yield f"data: {json.dumps(err_payload)}\n\n"

    @classmethod
    def apply(cls, server: DevServer):
        """Bind the patch to a DevServer instance."""
        server._stream_execution = cls.stream_execution.__get__(server, server.__class__)
        return server
