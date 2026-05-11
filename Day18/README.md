# Day 18 — Multi-Agent Workflow & Orchestration Choices

This folder holds **Day 18** coursework: a **three-agent workflow** design (researcher → writer → reviewer) and a written **comparison** of **Semantic Kernel** versus **direct LLM/API calls**.

## Deliverables

| Deliverable | File |
|-------------|------|
| Agent workflow design | [agent_workflow.md](agent_workflow.md) |
| Framework comparison (Semantic Kernel vs direct API) | [framework_comparison.md](framework_comparison.md) |

Start with **agent_workflow.md** for roles, contracts, sequencing, diagram, and failure handling. Then read **framework_comparison.md** for scenario-based guidance (three scenarios favoring each approach).

---

## Is code required?

**No.** The graded deliverables for Day 18 are the two markdown documents. The Python demo below is **optional** so you can run the pipeline once and see structured handoffs.

## Optional code samples

| File | Purpose |
|------|---------|
| [demo_three_agents.py](demo_three_agents.py) | Plain Python + optional OpenAI SDK: mock or `--live` (no Semantic Kernel). |
| [requirements.txt](requirements.txt) | Minimal: `openai` for `demo_three_agents.py --live`. |
| [demo_semantic_kernel_three_agents.py](demo_semantic_kernel_three_agents.py) | **Semantic Kernel** version: `@kernel_function` HR “tool”, `Kernel.invoke`, then `invoke_prompt` for researcher → writer → reviewer in `--live` mode; `--mock` keeps LLM stubs but still exercises SK + plugin. |
| [requirements-semantic-kernel.txt](requirements-semantic-kernel.txt) | Pulls **`semantic-kernel`** (heavier dependency chain than `requirements.txt`). |

Run mock (works immediately with Python 3.10+):

```bash
cd Day18
python demo_three_agents.py --pretty
```

Run live — **Groq** (OpenAI-compatible SDK) or **OpenAI**:

```bash
pip install -r requirements.txt
# Groq:
set GROQ_API_KEY=your_groq_key
set GROQ_MODEL=llama-3.3-70b-versatile
python demo_three_agents.py --live --pretty
# OpenAI:
set OPENAI_API_KEY=your_key_here
set OPENAI_MODEL=gpt-4o-mini
python demo_three_agents.py --live --pretty
```

If both `GROQ_API_KEY` and `OPENAI_API_KEY` are set, **Groq is used**. On PowerShell: `$env:GROQ_API_KEY="..."`. **Do not paste keys into `.py` files** — use env vars or a local `.env` that is gitignored.

### Semantic Kernel demo (`demo_semantic_kernel_three_agents.py`)

Install the SK stack:

```bash
cd Day18
python -m pip install -r requirements-semantic-kernel.txt
```

Run **mock** (uses `Kernel`, native plugin via `invoke`, no LLM cost):

```bash
python demo_semantic_kernel_three_agents.py --mock --pretty
```

Run **live** (three `invoke_prompt` calls). Use **Groq** (`GROQ_API_KEY`, optional `GROQ_MODEL`) or **OpenAI** (`OPENAI_API_KEY`; model via `OPENAI_CHAT_MODEL_ID` or `OPENAI_MODEL`). If both keys exist, Groq wins.

```bash
python demo_semantic_kernel_three_agents.py --live --pretty
```

Official docs to go deeper: [Semantic Kernel docs](https://learn.microsoft.com/en-us/semantic-kernel/overview/), [Semantic Kernel repo (Python)](https://github.com/microsoft/semantic-kernel/tree/main/python).

---

## What you need on your side

| If you… | You need… |
|---------|-----------|
| Submit only written work | Nothing beyond the two `.md` deliverables (and this README if your instructor asks for a folder overview). |
| Run the **mock** demo | [Python](https://www.python.org/downloads/) 3.10+ on your PATH; no API key, no `pip install`. |
| Run the **live** demo (plain script) | `GROQ_API_KEY` *(or* `OPENAI_API_KEY`*);* `python -m pip install -r requirements.txt`; optional `GROQ_MODEL` or `OPENAI_MODEL`. |
| Run the **Semantic Kernel** demo | `python -m pip install -r requirements-semantic-kernel.txt`; for `--live`, set `GROQ_API_KEY` or `OPENAI_API_KEY` (plus model env vars as in the docstrings). Azure OpenAI needs a different SK connector ([chat completion setup](https://learn.microsoft.com/en-us/semantic-kernel/concepts/ai-services/chat-completion/)). |
| Read more theory | `framework_comparison.md` + Microsoft [quick start](https://learn.microsoft.com/en-us/semantic-kernel/get-started/quick-start-guide). |

**Costs / compliance:** Live mode calls a paid API; use mock mode for zero cost.

**Secrets:** Do not commit API keys. Copy [`.env.example`](.env.example) to **`Day18/.env`** and set `GROQ_API_KEY=...` there (folder is listed in [`.gitignore`](.gitignore)). Both demos load `.env` automatically if `python-dotenv` is installed (`requirements.txt`). You can still use `$env:GROQ_API_KEY` in PowerShell if you prefer.
