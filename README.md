# Microsoft Agent Framework Playground 🧠

*Python + .NET Dual Runtime Labs*

A hands-on playground to explore the **Microsoft Agent Framework (MAF)** — Microsoft’s open-source SDK and runtime for building **AI agents and multi-agent workflows** in **Python and .NET**.

This repository provides parallel examples in both languages to demonstrate how MAF enables **local, offline AI experimentation** using **Docker Model Runner** or other OpenAI-compatible backends.

---

## 🔰 Roadmap

| Phase | Title                         | Goal / Outcome                                                                |
| ----- | ----------------------------- | ----------------------------------------------------------------------------- |
| 1     | **The Awakening**             | Minimal offline agent (Python & .NET).                                        |
| 2     | **Chat Loop**                 | Add conversation context and simple memory.                                   |
| 3     | **Agentic Loop**              | Demonstrate the Sense → Plan → Act → Reflect cycle.                           |
| 4     | **Workflows**                 | Build multi-step agent orchestration using MAF graph workflows.               |
| 5     | **Local LLM Integration**     | Demonstrated: run MAF agents on local models via Docker Model Runner or vLLM. |
| 6     | **Observability & Logs**      | Add introspection: trace, debug, and visualize agent runs.                    |
| 7     | **Multi-Agent Collaboration** | Manager–worker coordination patterns using workflow nodes.                    |

Each lab contains Python and .NET implementations for parity and cross-language exploration.

---

## 🛠️ Directory Overview

```bash
labs/
  python/
    P01_the_awakening/
      main.py
      README.md
    P02_chat_loop/
  dotnet/
    P01.TheAwakening/
      Program.cs
      Msaf.P01.TheAwakening.csproj
      README.md
    P02.ChatLoop
    Labs.Shared.Utils/
      Labs.Shared.Utils.csproj
    MicrosoftAgentFrameworkPlayground.sln
.env
requirements.txt
README.md
```

---

## 🔌 Requirements

| Component    | Tooling                                                   |
| ------------ | --------------------------------------------------------- |
| Python       | ≥ 3.12 · `pip install agentframework`                     |
| .NET         | ≥ 10.0 (pre-release) · `dotnet add package Microsoft.AgentFramework` |
| Local Models | Docker Model Runner / vLLM / llama.server                       |
| Optional     | `pip install agentframework-devui` (for visualization)    |

---

## 💬 Current Focus

The current milestone covers:

* Offline execution (local LLMs, no API keys)
* Conversation context and summarization (WIP)
* Single-agent reasoning and response streaming
* Preparing for MAF **workflow orchestration** in upcoming labs

---

## 🔍 Upcoming Labs

* **P03 Agentic Loop:** introduce the reasoning cycle.
* **P04 Workflows:** explore graph-based orchestration.
* **P05 Multi-Agent Collaboration:** run manager/worker patterns.
* **P06 Observability:** logging, tracing, and metrics.

---

## 📜 Articles

| # | Title                                                          | Focus                            |
| - | -------------------------------------------------------------- | -------------------------------- |
| 1 | *Microsoft Agent Framework Running Inside Docker Model Runner* | Offline runtime demo             |
| 2 | *Building a Local Chat Agent*                                  | Memory & context                 |
| 3 | *Agentic Reasoning with MAF*                                   | Sense–Plan–Act–Reflect           |
| 4 | *MAF Workflows*                                                | Orchestration & multi-step tasks |

---

### © 2025 Juan G. Carmona - MAF Playground Series





