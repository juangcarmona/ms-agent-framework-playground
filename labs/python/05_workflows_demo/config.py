# config.py
import os

MCP_GATEWAY_URL = os.getenv("MCP_GATEWAY_URL", "http://localhost:8811/mcp")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "http://localhost:12434/engines/llama.cpp/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "none")
MODEL_ID = os.getenv("MODEL_ID", "ai/gpt-oss:latest")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB   = os.getenv("POSTGRES_DB", "postgres")
DEVUI_PORT = int(os.getenv("DEVUI_PORT", "8000"))
DEVUI_HOST = os.getenv("DEVUI_HOST", "0.0.0.0")