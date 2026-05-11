"""
Optional Day 18 demo: researcher → writer → reviewer pipeline.

Default: MOCK mode (no API key, no packages beyond stdlib).

Optional: LIVE mode (--live) calls the chat completions API:
  • Groq (OpenAI-compatible): GROQ_API_KEY (optional GROQ_MODEL, default llama-3.3-70b-versatile).
  • OpenAI: OPENAI_API_KEY (optional OPENAI_MODEL, default gpt-4o-mini).
If both keys are set, Groq is used first.

Secrets: put keys in Day18/.env (see .env.example). Install: pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


def _load_local_env() -> None:
    """Load Day18/.env if present (pip install python-dotenv). .env is gitignored."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(Path(__file__).resolve().parent / ".env")


def _extract_json(text: str) -> dict[str, Any]:
    """Best-effort parse: raw JSON or first ```json ... ``` block."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if m:
        return json.loads(m.group(1).strip())
    raise ValueError(f"Could not parse JSON from model output:\n{text[:500]}...")


_GROQ_BASE_URL = "https://api.groq.com/openai/v1"
_GROQ_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def _live_llm(system: str, user: str) -> dict[str, Any]:
    try:
        from openai import OpenAI
    except ImportError as e:
        raise SystemExit(
            "Install dependencies: pip install -r requirements.txt"
        ) from e

    groq_key = os.environ.get("GROQ_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    if groq_key:
        client = OpenAI(api_key=groq_key, base_url=_GROQ_BASE_URL)
        model = os.environ.get("GROQ_MODEL", _GROQ_DEFAULT_MODEL)
    elif openai_key:
        client = OpenAI(api_key=openai_key)
        model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    else:
        raise SystemExit(
            "LIVE mode needs GROQ_API_KEY or OPENAI_API_KEY in the environment "
            "(never paste keys into source files)."
        )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    content = resp.choices[0].message.content or ""
    return _extract_json(content)


def mock_researcher(brief: dict[str, Any]) -> dict[str, Any]:
    topic = brief.get("topic", "unknown")
    return {
        "query_intent": brief.get("intent", ""),
        "retrieved_at": "2026-05-11T12:00:00Z",
        "facts": [
            {
                "statement": f"Policy on {topic} requires manager approval for blocks > 3 days.",
                "sources": [
                    {
                        "id": "s1",
                        "title": "Employee Handbook §Leave",
                        "uri": "internal://handbook/leave",
                        "excerpt": "...manager approval required for consecutive days > 3...",
                    }
                ],
            },
            {
                "statement": "Accrued balance must be checked in HRIS before approval.",
                "sources": [
                    {
                        "id": "s2",
                        "title": "HRIS FAQ",
                        "uri": "internal://hris/faq",
                        "excerpt": "Always verify leave_balance before submitting.",
                    }
                ],
            },
        ],
        "gaps": ["Blackout calendar for Q4 not attached."],
        "conflicts": [],
    }


def mock_writer(brief: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    audience = brief.get("audience", "employees")
    return {
        "format": brief.get("format", "memo"),
        "body_markdown": (
            f"### Leave request — quick guide ({audience})\n\n"
            "- Check your **accrued balance** in HRIS before applying [s2].\n"
            "- If you need **more than 3 consecutive days**, your **manager must approve** [s1].\n"
            "- Note: Q4 blackout dates were not confirmed in this pack; ask HR if unsure.\n"
        ),
        "citation_map": [
            {"claim_span": "accrued balance", "fact_id": "facts[1]"},
            {"claim_span": "more than 3 consecutive days", "fact_id": "facts[0]"},
        ],
        "open_questions": ["Confirm Q4 blackout dates with HR."],
    }


def mock_reviewer(
    brief: dict[str, Any], pack: dict[str, Any], draft: dict[str, Any]
) -> dict[str, Any]:
    gaps = pack.get("gaps") or []
    issues: list[dict[str, str]] = []
    if gaps:
        issues.append(
            {
                "severity": "med",
                "detail": "Research pack lists gaps; draft should not imply blackout dates are known.",
            }
        )
    body = draft.get("body_markdown", "")
    if "s1" not in body and "manager" in body.lower():
        issues.append(
            {
                "severity": "low",
                "detail": "Prefer explicit source markers [s1]/[s2] for auditability.",
            }
        )
    verdict = "approve" if not any(i["severity"] == "high" for i in issues) else "revise"
    return {
        "verdict": verdict,
        "issues": issues,
        "revision_hints": [
            "Keep disclaimer that blackout calendar was not retrieved.",
        ],
    }


def live_researcher(brief: dict[str, Any]) -> dict[str, Any]:
    system = (
        "You are the Researcher agent. Return ONLY valid JSON matching this shape: "
        '{"query_intent":"string","retrieved_at":"ISO-8601","facts":[{"statement":"string",'
        '"sources":[{"id":"string","title":"string","uri":"string","excerpt":"string"}]}],'
        '"gaps":["string"],"conflicts":[{"topic":"string","note":"string","sources":["s1"]}]}'
    )
    user = "Brief:\n" + json.dumps(brief, indent=2)
    return _live_llm(system, user)


def live_writer(brief: dict[str, Any], pack: dict[str, Any]) -> dict[str, Any]:
    system = (
        "You are the Writer agent. Use ONLY the research pack facts; do not invent policy. "
        "Return ONLY valid JSON: "
        '{"format":"memo|faq|email","body_markdown":"string",'
        '"citation_map":[{"claim_span":"string","fact_id":"string"}],'
        '"open_questions":["string"]}'
    )
    user = json.dumps({"brief": brief, "research_pack": pack}, indent=2)
    return _live_llm(system, user)


def live_reviewer(
    brief: dict[str, Any], pack: dict[str, Any], draft: dict[str, Any]
) -> dict[str, Any]:
    system = (
        "You are the Reviewer agent. Check grounding vs research pack and brief. "
        "Return ONLY valid JSON: "
        '{"verdict":"approve|revise|escalate","issues":[{"severity":"low|med|high",'
        '"detail":"string"}],"revision_hints":["string"]}'
    )
    user = json.dumps(
        {"brief": brief, "research_pack": pack, "draft": draft}, indent=2
    )
    return _live_llm(system, user)


def main() -> None:
    _load_local_env()

    parser = argparse.ArgumentParser(
        description="Three-agent demo (researcher → writer → reviewer)."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Call LLM API (Groq via GROQ_API_KEY or OpenAI via OPENAI_API_KEY); pip install openai",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON stages to stdout",
    )
    args = parser.parse_args()

    brief = {
        "intent": "Explain leave submission rules.",
        "topic": "annual leave",
        "audience": "employees",
        "format": "faq",
        "constraints": {"max_words": 200},
    }

    if args.live:
        if not (
            os.environ.get("GROQ_API_KEY") or os.environ.get("OPENAI_API_KEY")
        ):
            print(
                "LIVE mode needs GROQ_API_KEY or OPENAI_API_KEY in the environment.",
                file=sys.stderr,
            )
            raise SystemExit(1)

        run_researcher, run_writer, run_reviewer = (
            live_researcher,
            live_writer,
            live_reviewer,
        )
        mode = (
            "live (Groq)"
            if os.environ.get("GROQ_API_KEY")
            else "live (OpenAI)"
        )
    else:
        run_researcher, run_writer, run_reviewer = (
            mock_researcher,
            mock_writer,
            mock_reviewer,
        )
        mode = "mock (offline)"

    print(f"Mode: {mode}\n")

    pack = run_researcher(brief)
    draft = run_writer(brief, pack)
    review = run_reviewer(brief, pack, draft)

    out = {"brief": brief, "research_pack": pack, "draft": draft, "review": review}
    if args.pretty:
        print(json.dumps(out, indent=2))
    else:
        print("research_pack:", json.dumps(pack, indent=2)[:400], "...\n")
        print("draft.body_markdown:\n", draft.get("body_markdown", ""))
        print("review.verdict:", review.get("verdict"))
        print("review.issues:", review.get("issues"))


if __name__ == "__main__":
    main()
