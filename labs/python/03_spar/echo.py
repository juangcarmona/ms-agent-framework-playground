
import json
from colorama import Fore, Style, init
from collections import defaultdict
from agent_framework import (
    TextContent,
    TextReasoningContent,
    FunctionCallContent,
    FunctionResultContent,
    DataContent,
    ErrorContent,
    UsageContent,
)

init(autoreset=True)


class Echo:
    # === Public methods ===
    @staticmethod
    def system(text: str, nl: bool = True):
        Echo._write("⚙ :", text, Fore.LIGHTBLACK_EX, nl)

    @staticmethod
    def debug(text: str, nl: bool = True):
        Echo._write("🐛:", text, Fore.LIGHTWHITE_EX, nl)

    @staticmethod
    def info(text: str, nl: bool = True):
        Echo._write("ℹ :", text, Fore.CYAN, nl)

    @staticmethod
    def user(text: str, nl: bool = True):
        Echo._write("🧑:", text, Fore.YELLOW, nl)

    @staticmethod
    def agent(text: str, nl: bool = True):
        Echo._write("🤖:", text, Fore.GREEN, nl)

    @staticmethod
    def warn(text: str, nl: bool = True):
        Echo._write("⚠ :", text, Fore.MAGENTA, nl)

    @staticmethod
    def step(text: str, nl: bool = True):
        Echo._write("✔ :", text, Fore.LIGHTYELLOW_EX, nl)

    @staticmethod
    def error(text: str, nl: bool = True):
        Echo._write("⛔:", text, Fore.RED, nl)

    @staticmethod
    def done(text: str, nl: bool = True):
        Echo._write("✅:", text, Fore.CYAN, nl)



    # === Stream processing ===
    @staticmethod
    async def stream_agent_async(updates):
        """Stream and narrate agent updates using typed content classes."""
        in_agent_line = False
        call_buffer = defaultdict(list)  # call_id -> list of partial args

        async for update in updates:
            # Handle incremental text
            if getattr(update, "text", None):
                if not in_agent_line:
                    print(Fore.GREEN + "🤖: ", end="", flush=True)
                    in_agent_line = True
                print(update.text, end="", flush=True)
                continue

            contents = getattr(update, "contents", None)
            if not contents:
                continue

            if in_agent_line:
                print()
                in_agent_line = False

            for content in contents:
                # ─────────────────────────────
                # THINK
                # ─────────────────────────────
                if isinstance(content, TextReasoningContent):
                    Echo.step(f"[THINK] {content.text}")

                # ─────────────────────────────
                # FUNCTION CALL (buffered)
                # ─────────────────────────────
                elif isinstance(content, FunctionCallContent):
                    call_id = getattr(content, "call_id", None)
                    raw_args = content.arguments

                    # Collect partial updates
                    call_buffer[call_id].append(raw_args)

                    # Try to merge & print only when the args look complete
                    # or when a new name appears (naive but effective)
                    if isinstance(raw_args, str) and raw_args.endswith("}"):
                        try:
                            merged_args_str = "".join(
                                a if isinstance(a, str) else json.dumps(a)
                                for a in call_buffer[call_id]
                            )
                            args = json.loads(merged_args_str)
                        except Exception:
                            args = {"_raw": merged_args_str}

                        args_str = " ".join(f"{k}={Echo._format_arg(v)}" for k, v in args.items())
                        Echo.step(f"[ACT] {content.name}({args_str})")
                        call_buffer.pop(call_id, None)

                # ─────────────────────────────
                # TOOL RESULT
                # ─────────────────────────────
                elif isinstance(content, FunctionResultContent):
                    # try several fallbacks to extract useful data
                    result = content.result

                    # 1️⃣ if result is None, try raw_representation
                    if result is None and getattr(content, "raw_representation", None):
                        raw = content.raw_representation
                        if isinstance(raw, dict):
                            # sometimes it's {"result": {...}} or {"content": "..."}
                            result = raw.get("result") or raw.get("content") or raw
                        else:
                            result = raw

                    # 2️⃣ if still None, check additional_properties
                    if result is None and getattr(content, "additional_properties", None):
                        result = content.additional_properties

                    # 3️⃣ if still nothing, mark as no data
                    if result is None or result == {}:
                        Echo.warn(f"[TOOL] {content.call_id} → (no data)")
                    else:
                        Echo.system(f"[TOOL] {content.call_id} → {Echo._to_preview(result)}")

                    # 4️⃣ if there’s an exception, log it too
                    if getattr(content, "exception", None):
                        Echo.error(f"[TOOL ERROR] {content.call_id} → {content.exception}")

                # ─────────────────────────────
                # TEXT
                # ─────────────────────────────
                elif isinstance(content, TextContent):
                    Echo.agent(content.text)

                # ─────────────────────────────
                # DATA
                # ─────────────────────────────
                elif isinstance(content, DataContent):
                    Echo.system(f"[DATA] {Echo._to_preview(content.data)}")

                # ─────────────────────────────
                # ERROR
                # ─────────────────────────────
                elif isinstance(content, ErrorContent):
                    Echo.error(f"[ERROR] {content.message}")

                # ─────────────────────────────
                # USAGE
                # ─────────────────────────────
                elif isinstance(content, UsageContent):
                    usage_dict = content.to_dict(exclude={"raw_representation"}, exclude_none=True)
                    Echo.info(f"[USAGE] {json.dumps(usage_dict, ensure_ascii=False)}")

                # ─────────────────────────────
                # UNKNOWN
                # ─────────────────────────────
                else:
                    cname = content.__class__.__name__
                    Echo.warn(f"[UNKNOWN] {cname}")

        # If still printing agent text
        if in_agent_line:
            print(Style.RESET_ALL)


    # === Helpers ===
    @staticmethod
    def _write(symbol: str, msg: str, color: str, nl: bool):
        end = "\n" if nl else ""
        print(color + symbol + " " + msg + Style.RESET_ALL, end=end)

    @staticmethod
    def _format_arg(value):
        if value is None:
            return "null"
        if isinstance(value, (str, int, float, bool)):
            return str(value).lower() if isinstance(value, bool) else str(value)
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)

    @staticmethod
    def _to_preview(obj, max_len: int = 240):
        if obj is None:
            return "(null)"
        try:
            s = json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj
        except Exception:
            s = str(obj)
        return s if len(s) <= max_len else s[:max_len] + "…"