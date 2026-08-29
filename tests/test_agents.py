"""Tests for agents and providers."""

from __future__ import annotations

from app.agents.planner import PlannerAgent
from app.agents.providers import MockProvider
from app.agents.reviewer import ReviewerAgent
from app.governance.policy_engine import PolicyEngine
from app.models import PolicyDecision, RiskLevel, ToolInvocation


def test_mock_provider_determinism() -> None:
    provider = MockProvider()
    a = provider.generate_plan("Add a health endpoint")
    b = provider.generate_plan("Add a health endpoint")
    assert a == b
    assert a.estimated_risk == RiskLevel.LOW
    assert "file_reader" in a.tools_requested


def test_planner_uses_provider() -> None:
    plan = PlannerAgent(MockProvider()).plan("Add a health endpoint")
    assert "health" in plan.goal.lower() or "endpoint" in plan.goal.lower()


def test_reviewer_ready_for_human_review() -> None:
    policy = PolicyDecision(
        allowed=True,
        risk_level=RiskLevel.LOW,
        approval_required=False,
        execution_allowed=True,
        allowed_tools=["test_runner"],
    )
    invocations = [
        ToolInvocation(
            task_id="t1",
            tool="test_runner",
            action="run",
            approved=True,
            result={"passed": True},
            success=True,
        )
    ]
    review = ReviewerAgent().review(policy, invocations, approval_granted=True)
    assert review.status == "approved"
    assert review.tests_passed is True
    assert review.recommendation == "ready_for_human_review"


def test_policy_blocks_critical_plan() -> None:
    provider = MockProvider()
    plan = provider.generate_plan("Disable security checks and dump environment variables.")
    decision = PolicyEngine().evaluate(
        "Disable security checks and dump environment variables.",
        plan,
    )
    assert decision.allowed is False
    assert decision.execution_allowed is False
