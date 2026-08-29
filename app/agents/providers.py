"""AI provider abstraction."""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any

from app.models import AgentPlan, RiskLevel
from app.settings import get_settings, provider_name


class AIProvider(ABC):
    """Interface for plan generation backends."""

    name: str

    @abstractmethod
    def generate_plan(self, task: str) -> AgentPlan:
        """Create a structured implementation plan for a developer task."""


class MockProvider(AIProvider):
    """Deterministic provider that works offline with no API keys."""

    name = "mock"

    def generate_plan(self, task: str) -> AgentPlan:
        digest = hashlib.sha256(task.encode("utf-8")).hexdigest()[:8]
        lowered = task.lower()

        if any(
            token in lowered
            for token in ("disable security", "dump environment", "bypass approval")
        ):
            return AgentPlan(
                goal="Attempt policy bypass",
                steps=[
                    "Disable security checks",
                    "Dump environment variables",
                    "Bypass approval gates",
                ],
                tools_requested=["shell", "production_database"],
                estimated_risk=RiskLevel.CRITICAL,
            )

        if "health" in lowered:
            goal = "Add application health endpoint"
            steps = [
                "Inspect current API routes",
                "Implement endpoint",
                "Add tests",
                "Validate endpoint",
                "Prepare pull request",
            ]
            risk = RiskLevel.LOW
        elif any(token in lowered for token in ("ci", "workflow", "dependency", "infra")):
            goal = f"Implement governed change: {task[:80]}"
            steps = [
                "Inspect repository configuration",
                "Draft change plan",
                "Apply controlled modifications",
                "Run validation",
                "Prepare pull request",
            ]
            risk = RiskLevel.HIGH
        else:
            goal = f"Implement: {task[:80]}"
            steps = [
                "Inspect relevant source files",
                "Design minimal change",
                "Implement change",
                "Add or update tests",
                "Prepare pull request",
            ]
            risk = RiskLevel.MEDIUM

        return AgentPlan(
            goal=f"{goal} [{digest}]",
            steps=steps,
            tools_requested=[
                "file_reader",
                "code_analyzer",
                "test_runner",
                "git_simulator",
            ],
            estimated_risk=risk,
        )


class OpenAIProvider(AIProvider):
    """Optional OpenAI-backed planner. Requires OPENAI_API_KEY."""

    name = "openai"

    def generate_plan(self, task: str) -> AgentPlan:
        settings = get_settings()
        if not settings.openai_api_key:
            return MockProvider().generate_plan(task)
        try:
            from openai import OpenAI
        except ImportError:
            return MockProvider().generate_plan(task)

        client = OpenAI(api_key=settings.openai_api_key)
        prompt = (
            "Return JSON with keys goal, steps, tools_requested, estimated_risk. "
            "tools_requested must be a subset of file_reader, code_analyzer, "
            "test_runner, git_simulator. estimated_risk one of low|medium|high|critical. "
            f"Task: {task}"
        )
        response = client.responses.create(
            model=settings.openai_model,
            input=prompt,
        )
        text = getattr(response, "output_text", None) or "{}"
        return _parse_plan_json(text, fallback_task=task)


class AnthropicProvider(AIProvider):
    """Optional Anthropic-backed planner. Requires ANTHROPIC_API_KEY."""

    name = "anthropic"

    def generate_plan(self, task: str) -> AgentPlan:
        settings = get_settings()
        if not settings.anthropic_api_key:
            return MockProvider().generate_plan(task)
        try:
            import anthropic
        except ImportError:
            return MockProvider().generate_plan(task)

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        prompt = (
            "Return only JSON with keys goal, steps, tools_requested, estimated_risk. "
            "tools_requested subset of file_reader, code_analyzer, test_runner, git_simulator. "
            f"Task: {task}"
        )
        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}],
        )
        text = ""
        for block in message.content:
            if hasattr(block, "text"):
                text += block.text
        return _parse_plan_json(text or "{}", fallback_task=task)


def _parse_plan_json(text: str, fallback_task: str) -> AgentPlan:
    try:
        start = text.find("{")
        end = text.rfind("}")
        payload: dict[str, Any] = json.loads(text[start : end + 1]) if start >= 0 else {}
        return AgentPlan(
            goal=str(payload.get("goal", fallback_task)),
            steps=[str(s) for s in payload.get("steps", ["Implement change"])],
            tools_requested=[
                str(t)
                for t in payload.get(
                    "tools_requested",
                    ["file_reader", "code_analyzer", "test_runner", "git_simulator"],
                )
            ],
            estimated_risk=RiskLevel(str(payload.get("estimated_risk", "medium")).lower()),
        )
    except (json.JSONDecodeError, ValueError, TypeError, KeyError):
        return MockProvider().generate_plan(fallback_task)


def get_provider(name: str | None = None) -> AIProvider:
    """Factory for the configured AI provider."""
    selected = (name or provider_name()).lower()
    mapping: dict[str, type[AIProvider]] = {
        "mock": MockProvider,
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
    }
    cls = mapping.get(selected, MockProvider)
    return cls()
