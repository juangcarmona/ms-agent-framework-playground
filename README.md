# Microsoft Agent Framework Playground 🧠

*Python + .NET Dual Runtime Edition*

A hands-on playground to explore the **Microsoft Agent Framework (MAF)** — Microsoft’s new open-source SDK for building **AI agents and multi-agent workflows**.

This playground demonstrates both **Python** and **.NET** flavours side-by-side, and how MAF could power **Sentra Brain’s agentic runtime** — from simple chat to multi-agent, fully local orchestration.

---

## 🦭 Roadmap

| Phase | Title                        | Description                             |
| ----- | ---------------------------- | --------------------------------------- |
| 1     | **Hello Agent**              | Minimal agent example (Python & .NET).  |
| 2     | **Chat Loop**                | Add context and memory.                 |
| 3     | **Agentic Loop**             | Implement Sense–Plan–Act–Reflect.       |
| 4     | **Multi-Agent Workflow**     | Manager–worker collaboration.           |
| 5     | **Local LLM Integration**    | Use vLLM / Docker Model Runner.         |
| 6     | **Custom Agents**            | Declarative YAML / JSON definitions.    |
| 7     | **Visual Workflows**         | DevUI or VSCode visualization.          |
| 8     | **Sentra Brain Integration** | Connecting MAF runtime to Sentra Brain. |

Each phase has a `python/` and `dotnet/` folder with its own README and runnable code.

---

## 🧱 Directory Overview

```bash
phases/
  01_hello_agent/
    python/ → minimal agent in Python
    dotnet/ → same logic implemented in C#
common/
  docker/ → vLLM or Model Runner setups
  configs/ → shared YAML agents/workflows
```

---

## ⚙️ Quick Start

### Python

```bash
pip install -r requirements.txt
python phases/01_hello_agent/python/main.py
```

### .NET

```bash
cd phases/01_hello_agent/dotnet
dotnet run
```

To run locally with your own model:

```bash
export OPENAI_API_BASE=http://localhost:1234/v1
export OPENAI_API_KEY=none
```

(Use [Docker Model Runner](https://docs.docker.com/desktop/ai/) or vLLM.)

---

## 🧩 Requirements

| Component    | Tooling                                                  |
| ------------ | -------------------------------------------------------- |
| Python       | ≥3.10 + `pip install agentframework`                     |
| .NET         | ≥8.0 SDK + `dotnet add package Microsoft.AgentFramework` |
| Optional     | `pip install agentframework-devui` (for visualization)   |
| Local Models | Docker Model Runner / vLLM containers                    |

---

## 🧠 Why Two Flavours?

Sentra Brain runs primarily on Python, but enterprise customers may prefer .NET microservices.
This playground tests both runtimes, showing **interoperability**, **local deployment**, and **cross-language workflow composition**.

---

## 🗞️ Article Series

| # | Title                                | Focus                     |
| - | ------------------------------------ | ------------------------- |
| 1 | *Meet Microsoft Agent Framework*     | Overview & setup          |
| 2 | *Building a Local Chat Agent*        | Chat loop                 |
| 3 | *Agentic Reasoning with MAF*         | Sense–Plan–Act–Reflect    |
| 4 | *Multi-Agent Workflows*              | Collaboration             |
| 5 | *Running MAF Locally*                | vLLM, Docker Model Runner |
| 6 | *Custom Agents for Private Copilots* | YAML declarative configs  |
| 7 | *Visualizing Workflows*              | DevUI / VSCode            |
| 8 | *MAF as Sentra Brain Runtime*        | Integration               |

---

## 🧩 Related Projects

* [Docker Cagent Playground](https://github.com/juangcarmona/cagent-playground)
* [Sentra Brain](https://github.com/sentra-brain/sentra-platform)

---

© 2025 Juan G. Carmona · Sentra Brain Playground Series
