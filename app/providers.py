"""AI provider abstraction with mock-first adapters."""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.config import Settings, get_settings

logger = logging.getLogger("eaeb.providers")


class AIProvider(ABC):
    name: str

    @abstractmethod
    def complete(self, system: str, user: str) -> str:
        raise NotImplementedError


class MockProvider(AIProvider):
    """Deterministic local provider for demos and CI. No network/credentials."""

    name = "mock"

    def complete(self, system: str, user: str) -> str:
        lower = user.lower()
        if "plan" in system.lower() or "create a plan" in lower:
            if any(k in lower for k in ("disable security", "dump environment", "exfiltrate")):
                return json.dumps(
                    {
                        "summary": "Requested actions conflict with governance policy.",
                        "steps": [
                            {
                                "id": "s1",
                                "description": "Evaluate request against security policy",
                                "tool_name": "policy.evaluate",
                                "risk": "CRITICAL",
                                "rationale": "Attempt to disable controls / dump secrets",
                            },
                            {
                                "id": "s2",
                                "description": "Dump environment variables",
                                "tool_name": "secrets.dump_env",
                                "risk": "CRITICAL",
                                "rationale": "Credential exposure",
                            },
                        ],
                        "overall_risk": "CRITICAL",
                        "estimated_manual_minutes": 30,
                        "estimated_ai_minutes": 5,
                        "notes": ["Malicious or unsafe intent detected in mock planner."],
                    }
                )
            return json.dumps(
                {
                    "summary": "Add a health endpoint exposing build metadata behind existing authz.",
                    "steps": [
                        {
                            "id": "s1",
                            "description": "Create feature branch",
                            "tool_name": "git.create_branch",
                            "risk": "LOW",
                            "rationale": "Isolated change set",
                        },
                        {
                            "id": "s2",
                            "description": "Implement /health endpoint with build metadata",
                            "tool_name": "code.apply_patch",
                            "risk": "MEDIUM",
                            "rationale": "Code change in API surface",
                        },
                        {
                            "id": "s3",
                            "description": "Run tests and security checks",
                            "tool_name": "ci.run_checks",
                            "risk": "LOW",
                            "rationale": "Quality gates",
                        },
                        {
                            "id": "s4",
                            "description": "Open simulated pull request",
                            "tool_name": "git.open_pr",
                            "risk": "MEDIUM",
                            "rationale": "Git-based delivery",
                        },
                    ],
                    "overall_risk": "MEDIUM",
                    "estimated_manual_minutes": 90,
                    "estimated_ai_minutes": 25,
                    "notes": ["SIMULATION: timings are illustrative only."],
                }
            )
        if "review" in system.lower():
            return json.dumps(
                {
                    "approved": True,
                    "findings": ["Patch scoped to health endpoint.", "No secrets in diff."],
                    "security_pass": True,
                    "tests_pass": True,
                    "summary": "Reviewer accepts change set for merge after human PR review.",
                }
            )
        return json.dumps({"message": "mock response", "echo": user[:200]})


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY required when AI_PROVIDER=openai")
        self.api_key = api_key

    def complete(self, system: str, user: str) -> str:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Install optional dependency: pip install .[openai]") from exc
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or "{}"


class AnthropicProvider(AIProvider):
    name = "anthropic"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required when AI_PROVIDER=anthropic")
        self.api_key = api_key

    def complete(self, system: str, user: str) -> str:
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("Install optional dependency: pip install .[anthropic]") from exc
        client = Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=1200,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        parts: list[str] = []
        for block in message.content:
            text = getattr(block, "text", None)
            if text:
                parts.append(text)
        return "\n".join(parts) or "{}"


def get_provider(settings: Settings | None = None) -> AIProvider:
    cfg = settings or get_settings()
    provider = cfg.ai_provider.lower().strip()
    if provider == "mock":
        return MockProvider()
    if provider == "openai":
        return OpenAIProvider(cfg.openai_api_key)
    if provider == "anthropic":
        return AnthropicProvider(cfg.anthropic_api_key)
    logger.warning("Unknown AI_PROVIDER=%s; falling back to mock", provider)
    return MockProvider()


def parse_json_response(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(line for line in lines if not line.startswith("```"))
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            data = json.loads(text[start : end + 1])
        else:
            return {"raw": text}
    if isinstance(data, dict):
        return data
    return {"value": data}
