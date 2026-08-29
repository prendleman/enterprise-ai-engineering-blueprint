"""Shared domain models used across agents, governance, and API layers."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(StrEnum):
    RECEIVED = "received"
    PLANNING = "planning"
    POLICY_CHECK = "policy_check"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class EventType(StrEnum):
    TASK_STARTED = "task_started"
    PLAN_CREATED = "plan_created"
    POLICY_CHECKED = "policy_checked"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    TOOL_INVOKED = "tool_invoked"
    TOOL_BLOCKED = "tool_blocked"
    TESTS_STARTED = "tests_started"
    TESTS_COMPLETED = "tests_completed"
    SECURITY_CHECK_COMPLETED = "security_check_completed"
    PR_CREATED = "pr_created"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"


class AgentPlan(BaseModel):
    goal: str
    steps: list[str]
    tools_requested: list[str]
    estimated_risk: RiskLevel = RiskLevel.MEDIUM


class PolicyDecision(BaseModel):
    allowed: bool
    risk_level: RiskLevel
    approval_required: bool
    execution_allowed: bool
    violations: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    allowed_tools: list[str] = Field(default_factory=list)


class ToolInvocation(BaseModel):
    task_id: str
    tool: str
    action: str
    approved: bool
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    result: dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    blocked_reason: str | None = None


class ReviewResult(BaseModel):
    status: str
    tests_passed: bool
    security_checks_passed: bool
    policy_violations: list[str] = Field(default_factory=list)
    recommendation: str
    unresolved_risks: list[str] = Field(default_factory=list)


class ProductivityEstimate(BaseModel):
    """Simulated productivity model — not experimentally validated."""

    estimated_manual_minutes: int
    ai_assisted_minutes: int
    estimated_minutes_saved: int
    productivity_gain_percent: float
    label: str = "simulated_estimate"


class TaskRecord(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    task: str
    status: TaskStatus = TaskStatus.RECEIVED
    provider: str = "mock"
    plan: AgentPlan | None = None
    policy: PolicyDecision | None = None
    review: ReviewResult | None = None
    tool_invocations: list[ToolInvocation] = Field(default_factory=list)
    branch_name: str | None = None
    pr_url: str | None = None
    approval_granted: bool = False
    blocked_reason: str | None = None
    report: dict[str, Any] = Field(default_factory=dict)
    productivity: ProductivityEstimate | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC)
