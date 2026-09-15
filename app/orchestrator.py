"""Task orchestration across planner → policy → executor → reviewer."""

from __future__ import annotations

from app.agents import ExecutorAgent, PlannerAgent, ReviewerAgent
from app.models import (
    ApprovalDecision,
    ApprovalRequest,
    TaskCreate,
    TaskRecord,
    TaskStatus,
    ToolCallStatus,
    utc_now,
)
from app.providers import AIProvider, get_provider
from app.security import audit_event, detect_prompt_injection, redact_secrets
from app.telemetry import TelemetryStore
from app.tools import ToolRegistry, build_default_registry


class Orchestrator:
    def __init__(
        self,
        store: TelemetryStore,
        provider: AIProvider | None = None,
        registry: ToolRegistry | None = None,
        *,
        block_critical: bool = True,
    ) -> None:
        self.store = store
        self.provider = provider or get_provider()
        self.registry = registry or build_default_registry()
        self.planner = PlannerAgent(self.provider)
        self.executor = ExecutorAgent(self.registry, block_critical=block_critical)
        self.reviewer = ReviewerAgent(self.provider)
        self.tasks: dict[str, TaskRecord] = {}

    def submit(self, payload: TaskCreate) -> TaskRecord:
        description = redact_secrets(payload.description)
        title = redact_secrets(payload.title)
        task = TaskRecord(title=title, description=description, requested_by=payload.requested_by)
        flags = detect_prompt_injection(f"{title}\n{description}")
        task.injection_flags = flags
        task.events.append(audit_event("task_received", {"task_id": task.id, "flags": flags}))
        task.status = TaskStatus.PLANNING
        task.plan = self.planner.plan(task)
        task.events.append(
            audit_event(
                "plan_created",
                {"task_id": task.id, "risk": task.plan.overall_risk.value, "steps": len(task.plan.steps)},
            )
        )

        if task.plan.overall_risk.value == "CRITICAL" or flags:
            task.status = TaskStatus.BLOCKED
            task.blocked_reason = (
                "Blocked by governance: critical risk and/or prompt-injection indicators "
                f"{flags or ['critical_plan']}"
            )
            # Still attempt tool invocations to demonstrate hard blocks in the audit trail.
            task = self.executor.execute_plan(task)
            task.completed_at = utc_now()
            task.events.append(audit_event("task_blocked", {"task_id": task.id, "reason": task.blocked_reason}))
            self._persist(task, event="task_blocked")
            return task

        task.status = TaskStatus.EXECUTING
        task = self.executor.execute_plan(task)

        pending = [c for c in task.tool_calls if c.status == ToolCallStatus.PENDING_APPROVAL]
        if pending:
            for call in pending:
                approval = ApprovalRequest(
                    task_id=task.id,
                    tool_name=call.tool_name,
                    reason=call.message,
                    risk=call.risk,
                )
                task.approvals.append(approval)
            task.status = TaskStatus.AWAITING_APPROVAL
            self.store.record_event(task.id, "approval_pending", {"count": len(pending)})
            task.events.append(audit_event("awaiting_approval", {"task_id": task.id}))
            self._persist(task)
            return task

        if task.blocked_reason or any(c.status == ToolCallStatus.BLOCKED for c in task.tool_calls):
            task.status = TaskStatus.BLOCKED
            task.completed_at = utc_now()
            self._persist(task, event="task_blocked")
            return task

        return self._finalize(task)

    def decide_approval(self, task_id: str, approval_id: str, decision: ApprovalDecision) -> TaskRecord:
        task = self.tasks[task_id]
        approval = next(a for a in task.approvals if a.id == approval_id)
        approval.status = "approved" if decision.approve else "denied"
        approval.decided_by = decision.decided_by
        approval.decided_at = utc_now()
        event_name = "approval_granted" if decision.approve else "approval_denied"
        self.store.record_event(task.id, event_name, {"approval_id": approval_id, "by": decision.decided_by})
        task.events.append(audit_event(event_name, {"task_id": task.id, "approval_id": approval_id}))

        if not decision.approve:
            task.status = TaskStatus.REJECTED
            task.blocked_reason = decision.comment or "Approval denied"
            task.completed_at = utc_now()
            self._persist(task)
            return task

        approved_tools = {a.tool_name for a in task.approvals if a.status == "approved"}
        # Re-run only pending high-risk tools after approval.
        pending_names = {
            c.tool_name for c in task.tool_calls if c.status == ToolCallStatus.PENDING_APPROVAL
        }
        task.tool_calls = [c for c in task.tool_calls if c.status != ToolCallStatus.PENDING_APPROVAL]
        for name in pending_names:
            invocation = self.registry.invoke(
                name,
                {"task_id": task.id, "approved": True},
                approved=name in approved_tools,
            )
            task.tool_calls.append(invocation)
        return self._finalize(task)

    def _finalize(self, task: TaskRecord) -> TaskRecord:
        task.status = TaskStatus.REVIEWING
        task.review = self.reviewer.review(task)
        task.status = TaskStatus.COMPLETED if task.review.approved else TaskStatus.FAILED
        task.completed_at = utc_now()
        task.touch()
        task.events.append(
            audit_event(
                "task_completed",
                {"task_id": task.id, "status": task.status.value, "approved": task.review.approved},
            )
        )
        self._persist(task)
        return task

    def _persist(self, task: TaskRecord, event: str | None = None) -> None:
        task.touch()
        self.tasks[task.id] = task
        self.store.upsert_task(task)
        if event:
            self.store.record_event(task.id, event, {"status": task.status.value})

    def get(self, task_id: str) -> TaskRecord:
        return self.tasks[task_id]

    def list_tasks(self) -> list[TaskRecord]:
        return sorted(self.tasks.values(), key=lambda t: t.created_at, reverse=True)
