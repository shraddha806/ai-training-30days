"""
Semantic Kernel demo: researcher -> writer -> reviewer.

What you practice
-----------------
1. Kernel: add OpenAI chat completion service (live) or skip it (mock).
2. Native plugin: @kernel_function simulates HR "tool" retrieval (always runs via SK).
3. invoke + invoke_prompt: tool first, then three LLM stages (live) or PYTHON fallbacks (mock).

Install
-------
    python -m pip install -r requirements-semantic-kernel.txt

Mock (no API key; still uses Kernel + plugin)
----------------------------------------------
    python demo_semantic_kernel_three_agents.py --mock --pretty

Live (Groq OR OpenAI; never put keys inside this file — use env vars)
-----------------------------------------------------------------------
    python -m pip install -r requirements-semantic-kernel.txt

    Groq (OpenAI-compatible):
        set GROQ_API_KEY=your_groq_key
        set GROQ_MODEL=llama-3.3-70b-versatile
        python demo_semantic_kernel_three_agents.py --live --pretty

    OpenAI:
        set OPENAI_API_KEY=your_key
        set OPENAI_CHAT_MODEL_ID=gpt-4o-mini
        python demo_semantic_kernel_three_agents.py --live --pretty

    If both GROQ_API_KEY and OPENAI_API_KEY exist, Groq is used.

PowerShell: $env:GROQ_API_KEY="..."  or  $env:OPENAI_API_KEY="..."

Alternatively copy .env.example to .env under Day18/ (gitignored).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from semantic_kernel.functions import kernel_function


def _load_local_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(Path(__file__).resolve().parent / ".env")


SERVICE_ID = "default"
_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if m:
        return json.loads(m.group(1).strip())
    raise ValueError(f"Could not parse JSON from:\n{text[:800]}")


def _result_text(fr: Any) -> str:
    """Turn FunctionResult (or similar) into plain text."""
    if fr is None:
        return ""
    v = getattr(fr, "value", fr)
    if isinstance(v, list) and v:
        v = v[0]
    if hasattr(v, "content"):
        return (v.content or "") or str(v)
    return str(fr)


class HrResearchPlugin:
    """Simulated internal corpus (no HTTP). Demonstrates Semantic Kernel plugins."""

    @kernel_function(
        name="fetch_leave_facts",
        description=(
            "Returns structured JSON snippets from the internal HR knowledge base "
            "(policy excerpts only; not legal advice)."
        ),
    )
    def fetch_leave_facts(self) -> str:
        payload = {
            "retrieved_at": "2026-05-11T12:00:00Z",
            "snippets": [
                {
                    "id": "s1",
                    "title": "Handbook § Leave blocks",
                    "excerpt": "Manager approval required for consecutive annual leave exceeding 3 business days.",
                },
                {
                    "id": "s2",
                    "title": "HRIS guideline",
                    "excerpt": "Verify accrued leave_balance in HRIS before submitting a request.",
                },
            ],
            "gaps_note": "Official Q4 blackout calendar not synced to this corpus.",
        }
        return json.dumps(payload)


def _mock_pack_from_facts(facts_blob: dict[str, Any]) -> dict[str, Any]:
    return {
        "query_intent": "Explain leave rules from internal snippets.",
        "retrieved_at": facts_blob.get("retrieved_at", ""),
        "facts": [
            {
                "statement": "Manager approval required for consecutive annual leave over 3 business days.",
                "sources": [
                    {"id": "s1", "uri": "internal://handbook/leave", "excerpt": facts_blob["snippets"][0]["excerpt"]},
                ],
            },
            {
                "statement": "Check accrued balance in HRIS before submitting.",
                "sources": [
                    {"id": "s2", "uri": "internal://hris", "excerpt": facts_blob["snippets"][1]["excerpt"]},
                ],
            },
        ],
        "gaps": [facts_blob.get("gaps_note", "")],
        "conflicts": [],
    }


def _mock_writer_pack(brief: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    return {
        "format": brief.get("format", "faq"),
        "body_markdown": (
            "### Leave requests\n\n"
            "- Confirm **leave balance** in HRIS before you apply.\n"
            "- **More than 3 consecutive business days** needs manager approval.\n"
            "- Q4 blackout list may be incomplete — confirm with HR if unsure.\n"
        ),
        "citation_map": [
            {"claim_span": "leave balance / HRIS", "fact_id": "s2"},
            {"claim_span": "3 consecutive business days", "fact_id": "s1"},
        ],
        "open_questions": ["Confirm Q4 blackout dates."],
    }


def _mock_review(brief: dict[str, Any], pack: dict[str, Any], draft: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if pack.get("gaps"):
        issues.append(
            {
                "severity": "low",
                "detail": "Research pack noted missing blackout calendar.",
            },
        )
    return {
        "verdict": "approve",
        "issues": issues,
        "revision_hints": [],
    }


def _build_kernel_with_llm_service(model_id: str) -> Any:
    """Register chat completion: Groq (OpenAI-compatible) if GROQ_API_KEY, else OpenAI."""
    from openai import AsyncOpenAI

    from semantic_kernel import Kernel
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

    kernel = Kernel()
    groq_key = os.environ.get("GROQ_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")

    if groq_key:
        kernel.add_service(
            OpenAIChatCompletion(
                service_id=SERVICE_ID,
                ai_model_id=model_id,
                async_client=AsyncOpenAI(
                    api_key=groq_key,
                    base_url=_GROQ_BASE_URL,
                ),
            )
        )
    elif openai_key:
        kernel.add_service(
            OpenAIChatCompletion(
                service_id=SERVICE_ID,
                ai_model_id=model_id,
                api_key=openai_key,
            )
        )
    else:
        raise RuntimeError(
            "Set GROQ_API_KEY or OPENAI_API_KEY in the environment "
            "(do not store API keys in source files)."
        )
    return kernel


async def _run_native_tool(kernel: Any) -> dict[str, Any]:
    fn = kernel.get_function("HrResearch", "fetch_leave_facts")
    from semantic_kernel.functions.kernel_arguments import KernelArguments

    res = await kernel.invoke(function=fn, arguments=KernelArguments())
    return json.loads(str(res.value))


async def _llm_research_pack(kernel: Any, brief: dict[str, Any], facts_blob: dict[str, Any]) -> dict[str, Any]:
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

    schema = (
        '{"query_intent":"string","retrieved_at":"string","facts":[{"statement":"string",'
        '"sources":[{"id":"string","title":"string","uri":"string","excerpt":"string"}]}],'
        '"gaps":["string"],"conflicts":[]}'
    )
    prompt = (
        "You are the Researcher agent. Normalize the INTERNAL_JSON into a research pack. "
        "Use only information present in INTERNAL_JSON.\nReturn ONLY valid JSON matching:\n"
        f"{schema}\n\nINTERNAL_JSON:\n"
        + json.dumps(facts_blob)
        + "\n\nBrief:\n"
        + json.dumps(brief)
    )

    exec_settings = OpenAIChatPromptExecutionSettings(
        service_id=SERVICE_ID,
        max_tokens=1200,
        temperature=0.2,
    )
    fr = await kernel.invoke_prompt(prompt=prompt, settings=exec_settings)
    return _extract_json(_result_text(fr))


async def _llm_writer(kernel: Any, brief: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

    schema = (
        '{"format":"string","body_markdown":"string",'
        '"citation_map":[{"claim_span":"string","fact_id":"string"}],'
        '"open_questions":["string"]}'
    )
    prompt = (
        "You are the Writer agent. Write for the brief using ONLY facts in RESEARCH_PACK. "
        "If something is unknown, note it under open_questions.\nReturn ONLY JSON:\n"
        f"{schema}\n\nBRIEF:\n{json.dumps(brief)}\n\nRESEARCH_PACK:\n{json.dumps(pack)}"
    )

    exec_settings = OpenAIChatPromptExecutionSettings(
        service_id=SERVICE_ID,
        max_tokens=1200,
        temperature=0.3,
    )
    fr = await kernel.invoke_prompt(prompt=prompt, settings=exec_settings)
    return _extract_json(_result_text(fr))


async def _llm_reviewer(
    kernel: Any, brief: dict[str, Any], pack: dict[str, Any], draft: dict[str, Any]
) -> dict[str, Any]:
    from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings

    schema = (
        '{"verdict":"approve|revise|escalate","issues":[{"severity":"low|med|high",'
        '"detail":"string"}],"revision_hints":["string"]}'
    )
    prompt = (
        "You are the Reviewer. Check grounding: every strong factual claim must be supported "
        "by RESEARCH_PACK. Return ONLY JSON:\n"
        f"{schema}\n\nBRIEF:\n{json.dumps(brief)}\n\nRESEARCH_PACK:\n{json.dumps(pack)}\n\n"
        "DRAFT:\n"
        + json.dumps(draft)
    )

    exec_settings = OpenAIChatPromptExecutionSettings(
        service_id=SERVICE_ID,
        max_tokens=800,
        temperature=0.1,
    )
    fr = await kernel.invoke_prompt(prompt=prompt, settings=exec_settings)
    return _extract_json(_result_text(fr))


async def _async_main(use_live_llm: bool, pretty: bool) -> None:
    from semantic_kernel import Kernel

    kernel = Kernel()
    kernel.add_plugin(HrResearchPlugin(), plugin_name="HrResearch")

    facts_blob = await _run_native_tool(kernel)

    brief: dict[str, Any] = {
        "intent": "Explain annual leave submission for employees.",
        "audience": "employees",
        "format": "faq",
        "constraints": {"max_words": 220},
    }

    if use_live_llm:
        groq_key = os.environ.get("GROQ_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not groq_key and not openai_key:
            print(
                "LIVE needs GROQ_API_KEY or OPENAI_API_KEY (see module docstring).",
                file=sys.stderr,
            )
            raise SystemExit(1)

        if groq_key:
            model = (
                os.environ.get("GROQ_MODEL")
                or os.environ.get("OPENAI_CHAT_MODEL_ID")
                or os.environ.get("OPENAI_MODEL")
                or _GROQ_DEFAULT_MODEL
            )
        else:
            model = (
                os.environ.get("OPENAI_CHAT_MODEL_ID")
                or os.environ.get("OPENAI_MODEL")
                or "gpt-4o-mini"
            )

        kernel = _build_kernel_with_llm_service(model)
        kernel.add_plugin(HrResearchPlugin(), plugin_name="HrResearch")
        facts_blob = await _run_native_tool(kernel)

        pack = await _llm_research_pack(kernel, brief, facts_blob)
        draft = await _llm_writer(kernel, brief, pack)
        review = await _llm_reviewer(kernel, brief, pack, draft)
        backend = "Groq" if groq_key else "OpenAI"
        mode = f"Semantic Kernel live ({backend}, model={model})"
    else:
        pack = _mock_pack_from_facts(facts_blob)
        draft = _mock_writer_pack(brief, pack)
        review = _mock_review(brief, pack, draft)
        mode = "Semantic Kernel mock (plugin via SK; stages with Python stubs)"

    out = {
        "mode": mode,
        "native_tool_raw": facts_blob,
        "brief": brief,
        "research_pack": pack,
        "draft": draft,
        "review": review,
    }
    print(f"Mode: {mode}\n")
    print(json.dumps(out, indent=2) if pretty else json.dumps(out))


def main() -> None:
    _load_local_env()

    p = argparse.ArgumentParser(
        description="Semantic Kernel pipeline: HR plugin tool + researcher/writer/reviewer."
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument(
        "--mock",
        action="store_true",
        help="Invoke native plugin via SK; researcher/writer/reviewer use offline stubs.",
    )
    g.add_argument(
        "--live",
        action="store_true",
        help="Three LLM steps via SK invoke_prompt (Groq or OpenAI env keys).",
    )
    p.add_argument("--pretty", action="store_true", help="Indent JSON.")
    args = p.parse_args()

    asyncio.run(_async_main(use_live_llm=args.live, pretty=args.pretty))


if __name__ == "__main__":
    main()
