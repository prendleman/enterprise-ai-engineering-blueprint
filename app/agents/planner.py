"""Planner agent — produces structured implementation plans."""

from __future__ import annotations

from app.agents.providers import AIProvider, get_provider
from app.models import AgentPlan


class PlannerAgent:
    """Generate an implementation plan for a developer request."""

    def __init__(self, provider: AIProvider | None = None) -> None:
        self.provider = provider or get_provider()

    def plan(self, task: str) -> AgentPlan:
        return self.provider.generate_plan(task)
