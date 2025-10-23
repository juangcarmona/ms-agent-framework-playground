# Microsoft Agent Framework Playground 🧠  
*Python + .NET Dual Runtime Labs*

A hands-on playground to explore the **Microsoft Agent Framework (MAF)** — Microsoft’s open-source SDK and runtime for building **AI agents and multi-agent workflows** in **Python** and **.NET**.

> This repository provides parallel experiments in both runtimes, showing how MAF enables **local, offline, and privacy-first AI execution** powered by **Docker Model Runner (DMR)** but other **OpenAI-compatible local backends** such as `vLLM` or `llama.cpp` could be used instead.

---

## 🔰 Roadmap

| Phase | Title                             | Goal / Outcome                                                                                                                   | Article / Reference |
| ----- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------- |
| 1     | **The Awakening**                 | Minimal offline agent (Python + . NET) running locally via Docker Model Runner.                                                 | [Run Agent Framework Locally](https://jgcarmona.com/run-agent-framework-locally/) |
| 2     | **Chat Loop**                     | Adds conversation context and simple persistence (C# only).                                                                    | [Building a Local Chat Agent (.NET)](https://jgcarmona.com/building-local-chat-agent-microsoft-agent-framework-dotnet/) |
| 3     | **Agentic Loop (SPAR)**           | Implements the Sense → Plan → Act → Reflect cycle and reasoning loop.                                                          | [Agentic Reasoning with MAF](https://jgcarmona.com/agentic-reasoning-with-microsoft-agent-framework/) · [AI Agents in a Nutshell](https://jgcarmona.com/ai-agents-nutshell/) |
| 4     | **DevUI + MCP Gateway**           | Integrates MCP tools and Docker MCP Servers inside MAF DevUI using custom streaming gateway and client.                         | [MAF + DevUI + Docker MCP Gateway with DMR](https://jgcarmona.com/maf-devui-docker-mcp-gateway-dmr/) |
| 5     | **Workflows and Persistence**     | Demonstrates multi-step agentic workflows with checkpointing (PostgreSQL), multi-agent collaboration and tool integration.     | [Building Agentic Workflows with MAF and DMR](https://jgcarmona.com/building-workflows-with-maf-and-dmr/) |
| 6     | **Observability & Orchestration** | (Planned) Add logs, traces and visualization of workflow runs; define multi-agent coordination patterns and monitoring.         | — |

Each lab evolves incrementally, building on the previous one while maintaining parity between Python and .NET where possible.

---

## 🛠️ Directory Overview

```bash
labs/
  dotnet/
    01_the_awakening/
    02_persistence/
      Msaf02Persistence/
    03_spar/
    Labs.Shared.Utils/

  python/
    01_the_awakening/
    03_spar/
    04_devui_with_mcp/
    05_workflows_demo/
      main.py
      docker-compose.yml
      agents/
      persistence/
      tools/
      workflows/
.env
requirements.txt
docker-compose.yml
README.md
```

## 🔌 Requirements

| Component        | Tooling                                                              |
| ---------------- | -------------------------------------------------------------------- |
| **Python**       | ≥ 3.12 · `pip install agentframework` (ore requirements.txt per lab) |
| **.NET**         | ≥ 10.0 (pre-release) · `dotnet add package Microsoft.AgentFramework` |
| **Local Models** | Docker Model Runner / vLLM / llama.server                            |
| **Optional**     | `pip install agentframework-devui` (for workflow visualization)      |


## 💬 Current Focus

* Fully offline execution (no API keys, no cloud dependencies).
* Multi-step workflows with PostgreSQL checkpoint storage.
* Multi-agent collaboration via tools and MCP Gateway servers.
* Integration of built-in filesystem and system tools.
* Persistent MCP sessions and streaming support within DevUI.


## 🔍 Upcoming Labs

| # | Title                         | Focus                                                            |
| - | ----------------------------- | ---------------------------------------------------------------- |
| 6 | **Observability & Logs**      | Introduce tracing, workflow introspection and run-time metrics.  |
| 7 | **Multi-Agent Orchestration** | Explore manager/worker coordination patterns and shared context. |

---

## 📜 Articles

| # | Title                                                                                                                   | Focus                                                     |
| - | ----------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| 1 | [Run Agent Framework Locally](https://jgcarmona.com/run-agent-framework-locally/)                                       | Offline runtime setup with DMR (“The Awakening”).         |
| 2 | [Building a Local Chat Agent (.NET)](https://jgcarmona.com/building-local-chat-agent-microsoft-agent-framework-dotnet/) | Conversation context and memory loop.                     |
| 3 | [Agentic Reasoning with MAF](https://jgcarmona.com/agentic-reasoning-with-microsoft-agent-framework/)                   | SPAR loop – Sense, Plan, Act, Reflect.                    |
| 4 | [Using MCP with Microsoft Agent Framework](https://jgcarmona.com/using-mcp-with-microsoft-agent-framework/)             | MCP StdioTools, local tool execution and lessons learned. |
| 5 | [MAF + DevUI + Docker MCP Gateway with DMR](https://jgcarmona.com/maf-devui-docker-mcp-gateway-dmr/)                    | DevUI integration and MCP Gateway workarounds.            |
| 6 | [Building Agentic Workflows with MAF and DMR](https://jgcarmona.com/building-workflows-with-maf-and-dmr/)               | Multi-step workflows, checkpointing and tool integration. |



### © 2025 Juan G. Carmona — MAF Playground Series

