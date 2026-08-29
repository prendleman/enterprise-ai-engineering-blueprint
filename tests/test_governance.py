"""Governance integration tests."""

from __future__ import annotations

from pathlib import Path

from app.agents.executor import ExecutorAgent
from app.governance.approvals import ApprovalService
from app.governance.policy_engine import PolicyEngine
from app.governance.risk import RiskEngine
from app.governance.tool_registry import ToolRegistry
from app.models import AgentPlan, PolicyDecision, RiskLevel
from app.telemetry.events import TelemetryService
from app.telemetry.repository import TelemetryRepository


def test_disabled_tools_cannot_execute(tmp_path: Path) -> None:
    repo = TelemetryRepository(tmp_path / "t.db")
    telemetry = TelemetryService(repo)
    executor = ExecutorAgent(telemetry=telemetry)
    policy = PolicyDecision(
        allowed=True,
        risk_level=RiskLevel.MEDIUM,
        approval_required=False,
        execution_allowed=True,
        allowed_tools=["shell"],
    )
    # Force shell into allowed list to prove runtime still blocks disabled tools
    results = executor.execute("task-1", "run shell", policy)
    assert results
    assert results[0].success is False
    assert results[0].blocked_reason is not None
    events = repo.list_events("task-1")
    assert any(event.event_type == "tool_blocked" for event in events)


def test_critical_risk_actions_are_blocked() -> None:
    plan = AgentPlan(
        goal="Bypass",
        steps=["dump secrets"],
        tools_requested=["shell"],
        estimated_risk=RiskLevel.CRITICAL,
    )
    decision = PolicyEngine().evaluate("access production database credentials", plan)
    assert decision.allowed is False
    assert decision.execution_allowed is False


def test_high_risk_actions_require_approval() -> None:
    assert ApprovalService().requires_approval(RiskLevel.HIGH) is True
    plan = AgentPlan(
        goal="Change CI",
        steps=["edit workflow"],
        tools_requested=["file_reader", "git_simulator"],
        estimated_risk=RiskLevel.HIGH,
    )
    decision = PolicyEngine().evaluate("Modify CI workflows and add dependency", plan)
    assert decision.approval_required is True
    assert decision.allowed is True


def test_tool_registry_allowlist() -> None:
    registry = ToolRegistry()
    assert registry.is_enabled("file_reader") is True
    assert registry.is_enabled("shell") is False
    allowed, blocked = registry.filter_allowed(["file_reader", "shell"])
    assert allowed == ["file_reader"]
    assert blocked == ["shell"]


def test_risk_engine_levels() -> None:
    engine = RiskEngine()
    assert engine.assess("inspect source files") in {RiskLevel.LOW, RiskLevel.MEDIUM}
    assert engine.assess("modify ci github actions terraform") == RiskLevel.HIGH
    assert engine.assess("disable security and reveal secrets") == RiskLevel.CRITICAL
