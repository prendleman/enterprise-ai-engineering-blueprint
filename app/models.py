"""Shared domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id(prefix: str = "id") -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TaskStatus(StrEnum):
    RECEIVED = "received"
    PLANNING = "planning"
    AWAITING_APPROVAL = "awaiting_approval"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    REJECTED = "rejected"


class ToolCallStatus(StrEnum):
    ALLOWED = "allowed"
    BLOCKED = "blocked"
    PENDING_APPROVAL = "pending_approval"
    EXECUTED = "executed"
    DENIED = "denied"
    FAILED = "failed"


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=3, max_length=4000)
    requested_by: str = "demo-user"


class TaskPlanStep(BaseModel):
    id: str
    description: str
    tool_name: str | None = None
    risk: RiskLevel = RiskLevel.LOW
    rationale: str = ""


class TaskPlan(BaseModel):
    summary: str
    steps: list[TaskPlanStep]
    overall_risk: RiskLevel
    estimated_manual_minutes: int
    estimated_ai_minutes: int
    notes: list[str] = Field(default_factory=list)


class ToolInvocation(BaseModel):
    id: str = Field(default_factory=lambda: new_id("tool"))
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    risk: RiskLevel
    status: ToolCallStatus
    result: dict[str, Any] | None = None
    message: str = ""
    created_at: datetime = Field(default_factory=utc_now)


class ApprovalRequest(BaseModel):
    id: str = Field(default_factory=lambda: new_id("apr"))
    task_id: str
    tool_name: str
    reason: str
    risk: RiskLevel
    status: str = "pending"
    decided_by: str | None = None
    decided_at: datetime | None = None


class ApprovalDecision(BaseModel):
    approve: bool
    decided_by: str = "human-reviewer"
    comment: str = ""


class ReviewResult(BaseModel):
    approved: bool
    findings: list[str] = Field(default_factory=list)
    security_pass: bool = True
    tests_pass: bool = True
    summary: str = ""


class TaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: new_id("task"))
    title: str
    description: str
    requested_by: str
    status: TaskStatus = TaskStatus.RECEIVED
    plan: TaskPlan | None = None
    tool_calls: list[ToolInvocation] = Field(default_factory=list)
    approvals: list[ApprovalRequest] = Field(default_factory=list)
    review: ReviewResult | None = None
    injection_flags: list[str] = Field(default_factory=list)
    events: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None
    branch_name: str | None = None
    pr_url: str | None = None
    blocked_reason: str | None = None

    def touch(self) -> None:
        self.updated_at = utc_now()


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    build_sha: str
    provider: str
    timestamp: datetime


class MetricsSnapshot(BaseModel):
    tasks_total: int
    tasks_completed: int
    tasks_blocked: int
    avg_completion_seconds: float
    simulated_pr_cycle_minutes: float
    test_pass_rate: float
    security_pass_rate: float
    tool_call_success_rate: float
    blocked_tool_attempts: int
    approvals_pending: int
    approvals_granted: int
    approvals_denied: int
    policy_violations: int
    high_risk_percentage: float
    simulated_manual_minutes: float
    simulated_ai_minutes: float
    simulated_minutes_saved: float
    note: str = (
        "Productivity timings are simulated for blueprint demos and are not experimentally validated."
    )
