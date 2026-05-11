# Day 18 — Semantic Kernel vs Direct API Calls

## 1. Definitions (short)

**Direct API calls** — Your code calls an LLM provider (e.g., Azure OpenAI, OpenAI, Anthropic) **directly**: HTTP/SDK, prompts, parsing responses, retries, orchestration loops, and tooling are mostly **your** responsibility unless you bolt on helpers.

[**Semantic Kernel (SK)**](https://learn.microsoft.com/en-us/semantic-kernel/overview/) — A Microsoft **SDK and patterns** layer for weaving LLMs together with **plugins** (skills), **planners**/sequencing, native function calling, connectors, telemetry hooks, filters, memory abstractions — aimed at evolving one-off demos into maintainable AI apps (.NET / Python/Java).

Neither replaces the underlying model APIs; SK **consumes** them (and hides some plumbing).

---

## 2. What to optimize for

| Dimension | Semantic Kernel leaning | Direct API leaning |
|-----------|-------------------------|---------------------|
| App surface | Larger app, evolving agents/workflows | Narrow script or micro-integration |
| Team | Invests in .NET/Python patterns and docs | Minimal framework surface |
| Control | Comfortable with conventions + hooks | Needs full control over every HTTP byte |
| Ecosystem | Microsoft/Azure alignment, connectors | Vendor-neutral glue |

Below: **three practical scenarios each** — when SK tends to earn its place, versus when straightforward API usage is clearer.

---

## 3. When Semantic Kernel tends to fit (three scenarios)

### Scenario A — Maintainable plugins and native function/tool orchestration

**Situation:** You expose many internal APIs (ticket lookup, entitlement check, wiki search) as model-callable functions. Prompts iterate weekly; junior devs add tools without rewriting raw HTTP wrappers each time.

**Why SK**

- Declarative **plugins** (`KernelFunction`, descriptions for the model).
- Structured **automatic function calling** and consistent patterns for chaining.
- **Filters** / interceptors let you centrally enforce logging, quota, PI redaction **before** the model executes the next round.

Direct API remains possible here but repeats more boilerplate and convention drift across services.

---

### Scenario B — Long-lived enterprise solution on Azure/Microsoft stack

**Situation:** .NET/Python service deployed on Azure AI / OpenAI enterprise keys, Entra ID, Application Insights — you expect memory, multimodal adapters, connectors to Microsoft graphs of services over time.

**Why SK**

- Aligns with **Microsoft’s agent and kernel samples**, enterprise docs, “kernel + planner + connectors” roadmap.
- **Memory** connectors and embeddings abstractions evolve with the ecosystem; less custom reinventing across teams.

Teams not on Microsoft infra may weigh SK against other hubs (LangChain/LlamaIndex/Autogen patterns) — SK’s edge is tighter **Microsoft-aligned** coherence.

---

### Scenario C — Regulated workloads needing consistent observability patterns

**Situation:** You must prove what the model requested, what tools ran, latency, retries, correlation ids — same structure for auditors across multiple agent features.

**Why SK**

- Central **lifecycle hooks** attach telemetry and policy normalization once.
- **Kernel** as a lifecycle object helps standardize “one run = one correlated trace spine” versus ad hoc wrappers per repo.

Again, you *can* do this entirely with APIs + OpenTelemetry wrappers; SK concentrates that into one supported pattern for teams already bought in.

---

## 4. When direct API calls tend to fit (three scenarios)

### Scenario D — One cron job, one prompt, one JSON response

**Situation:** Nightly “summarize these 20 rows from DB” with a single `chat.completions` call; no tools, no multi-agent graph.

**Why direct API**

- SK adds dependencies and concepts (kernel, plugins) with **no payoff** for a single linear call.
- Fewer moving parts in packaging, security review, and debugging.

---

### Scenario E — Hard dependency on a non-SK stack or language you don’t want to couple

**Situation:** Go/Rust/Node service with strict internal HTTP client layer, or you already standardized on another orchestration library (e.g., LangGraph, custom state machine).

**Why direct API**

- Use the **vendor SDK** you already ship; avoid second opinionated stack.
- SK is **.NET / Python / Java** — if your service is elsewhere, direct calls are natural.

---

### Scenario F — Maximum transparency and minimal magic

**Situation:** Research lab, security review, or novel sampling/reasoning where you hand-tune every token step, custom batching, or experimental router between several providers.

**Why direct API**

- **Full control** over prompts, headers, streaming, fallback ordering, and custom circuit breakers without framework defaults in the way.
- Easier to diff “exactly what we sent” for papers or incident postmortems.

---

## 5. Quick decision guide

```text
Start with direct API if:
  - Single call path, no tools, short script
  - Non-SK language or you already have another orchestrator
  - You need absolute minimal dependencies and full manual control

Consider Semantic Kernel if:
  - Growing catalog of tools/plugins and shared guardrails
  - Microsoft/Azure-oriented platform and long-term maintainability
  - You want kernel-level hooks for telemetry, filters, and consistent agent patterns
```

---

## 6. Final note

**Semantic Kernel does not replace your model provider** — it **structures** how your app composes prompts, functions, and policies. **Direct APIs** stay ideal for **small, linear, or highly custom** integrations. Many production systems use **direct calls in one service** and **orchestration frameworks in another**; the comparison above is about **fit**, not “always pick one.”

---

## 7. Hands-on in this repo (optional)

To see the same **researcher → writer → reviewer** shape side by side:

- **Direct API style:** [`demo_three_agents.py`](demo_three_agents.py) with optional OpenAI (`requirements.txt`).
- **Semantic Kernel:** [`demo_semantic_kernel_three_agents.py`](demo_semantic_kernel_three_agents.py) with a native **`@kernel_function` plugin** plus `Kernel.invoke_prompt` for the LLM steps (`requirements-semantic-kernel.txt`).

Run `--mock` on the SK demo to exercise the kernel and plugin without spending API credits.
