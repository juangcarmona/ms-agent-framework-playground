# Lab P03 – Agentic Reasoning

*A local mind starts thinking.*

Microsoft Agent Framework + Docker Model Runner + MCP tools = self-reflection, offline.

---

### 🎯 Goal

Implement the full **Sense → Plan → Act → Reflect (SPAR)** loop using
**Microsoft Agent Framework (MAF)** and **Docker Model Runner (DMR)**
with real **Model Context Protocol (MCP)** tools — **DuckDuckGo** and **Fetch Reference**.

The agent perceives, decides, acts, and verifies its own reasoning (see [AI Agents in a Nutshell](https://jgcarmona.com/ai-agents-nutshell/)) all **locally**. No API keys. No cloud. No tracking.

> **UPDATE (14 Oct 2025)**
> If your reasoning loops stop early or truncate mid-stream, DMR’s default context window (4K tokens) is the culprit.
> See this tip: [**How to Change Docker Model Runner Context Size — The Only Working Hack**](https://jgcarmona.com/change-dmr-context-size/)
> This tweak lets you push models like `ai/gpt-oss` to 128 K tokens and beyond.

> **NOTE 2:**
> Curious about **cagent** and declarative agents?
> Explore [**this repo**](https://github.com/juangcarmona/cagent-playground).

---

### ⚙️ Setup

1. **Enable Docker Model Runner** in Docker Desktop.
   To enable GPU acceleration, follow
   [Enable GPU for Docker Model Runner on Windows](https://jgcarmona.com/enable-gpu-docker-model-runner-windows/).

2. **Create and activate a Python environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Open the lab folder in VS Code** and use the built-in launch configuration.

> ⚠️ `.env` files are included **for educational purposes**.
> Never commit API keys or secrets in production.

---

### 🚀 Run

#### ▶️ From VS Code

Run **Lab P03 – Agentic Reasoning** from the **Run → Start Debugging** menu or press **F5**.

#### 🐳 Docker Compose

From this folder:

```bash
docker compose up
```

---

### 🧩 What Happens Under the Hood

* The agent launches two local **MCP servers** via Docker:
  `mcp/duckduckgo` and `mcp/fetch`.
* Each server is connected with `MCPStdioTool` inside a shared `async with` context,
  so the connection persists during the reasoning loop.
* The agent uses the **SPAR cycle**:

  1. **Sense →** understand the query
  2. **Plan →** choose tools and order
  3. **Act →** call DuckDuckGo and Fetch
  4. **Reflect →** summarize and verify coverage
* The `Echo` utility narrates every phase in color — `[THINK]`, `[CALL]`, `[TOOL]`, and final answers stream live.

> 💭 *When agents start reasoning locally,
> privacy and performance finally share the same loop.*

---

### 📚 References

* [Microsoft Agent Framework Playground (GitHub)](https://github.com/juangcarmona/ms-agent-framework-playground)
* [How to Change Docker Model Runner Context Size](https://jgcarmona.com/change-docker-model-runner-context-size/)
* [What is Docker cagent? A First Look at Declarative AI Agents](https://jgcarmona.com/what-is-docker-cagent-a-first-look-at-declarative-ai-agents/)
* [Memory in Docker cagent](https://jgcarmona.com/memory-in-docker-cagent/)

---

> 🧠 **Reasoning isn’t magic — it’s a loop.**

---

Would you like me to append a short **“Code Highlights”** section next (with the final working `async with duck, fetch, agent:` pattern and explanation of why it fixes MCP connectivity)? It would make the README even more practical for people cloning the repo.
