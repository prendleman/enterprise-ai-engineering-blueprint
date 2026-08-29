"""Task orchestration service — core governed agentic workflow."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from app.agents.executor import ExecutorAgent
from app.agents.planner import PlannerAgent
from app.agents.providers import get_provider
from app.agents.reviewer import ReviewerAgent
from app.governance.policy_engine import PolicyEngine
from app.logging_config import get_logger
from app.models import TaskRecord, TaskStatus
from app.settings import provider_name
from app.telemetry.events import TelemetryService
from app.telemetry.metrics import estimate_productivity
from app.telemetry.repository import TelemetryRepository

logger = get_logger(__name__)


class TaskService:
    """Coordinate plan → policy → approval → execute → review → metrics."""

    def __init__(
        self,
        repository: TelemetryRepository | None = None,
        telemetry: TelemetryService | None = None,
        planner: PlannerAgent | None = None,
        executor: ExecutorAgent | None = None,
        reviewer: ReviewerAgent | None = None,
        policy_engine: PolicyEngine | None = None,
    ) -> None:
        self.repository = repository or TelemetryRepository()
        self.telemetry = telemetry or TelemetryService(self.repository)
        self.planner = planner or PlannerAgent(get_provider())
        self.executor = executor or ExecutorAgent(telemetry=self.telemetry)
        self.reviewer = reviewer or ReviewerAgent()
        self.policy_engine = policy_engine or PolicyEngine()
        self._memory: dict[str, TaskRecord] = {}

    def create_task(self, task: str, *, auto_approve: bool = False) -> TaskRecord:
        """Accept a developer request and advance as far as policy allows."""
        record = TaskRecord(task=task, provider=provider_name(), status=TaskStatus.RECEIVED)
        self._memory[record.task_id] = record
        self.telemetry.emit(record.task_id, "task_started", {"task": task})
        self._persist(record)

        record.status = TaskStatus.PLANNING
        record.touch()
        plan = self.planner.plan(task)
        record.plan = plan
        self.telemetry.emit(
            record.task_id,
            "plan_created",
            plan.model_dump(mode="json"),
        )

        record.status = TaskStatus.POLICY_CHECK
        record.touch()
        policy = self.policy_engine.evaluate(task, plan)
        record.policy = policy
        self.telemetry.emit(
            record.task_id,
            "policy_checked",
            policy.model_dump(mode="json"),
        )

        if not policy.allowed or not policy.execution_allowed:
            record.status = TaskStatus.BLOCKED
            record.blocked_reason = "; ".join(policy.reasons) or "security policy violation"
            self.telemetry.emit(
                record.task_id,
                "task_failed",
                {"reason": record.blocked_reason, "status": "blocked"},
            )
            record.completed_at = datetime.now(UTC)
            record.report = self._build_report(record)
            self._persist(record)
            return record

        if policy.approval_required and not auto_approve:
            record.status = TaskStatus.AWAITING_APPROVAL
            self.telemetry.emit(
                record.task_id,
                "approval_requested",
                {"risk_level": policy.risk_level.value},
            )
            self._persist(record)
            return record

        if policy.approval_required and auto_approve:
            record.approval_granted = True
            self.telemetry.emit(record.task_id, "approval_granted", {"auto": True})

        return self._execute(record)

    def approve_task(self, task_id: str) -> TaskRecord:
        record = self.get_task(task_id)
        if record.status != TaskStatus.AWAITING_APPROVAL:
            raise ValueError(f"Task {task_id} is not awaiting approval")
        record.approval_granted = True
        record.status = TaskStatus.APPROVED
        record.touch()
        self.telemetry.emit(record.task_id, "approval_granted", {})
        return self._execute(record)

    def get_task(self, task_id: str) -> TaskRecord:
        if task_id in self._memory:
            return self._memory[task_id]
        row = self.repository.get_task(task_id)
        if not row:
            raise KeyError(task_id)
        record = self._row_to_record(row)
        self._memory[task_id] = record
        return record

    def list_events(self, task_id: str) -> list[dict[str, Any]]:
        return self.telemetry.events_for(task_id)

    def _execute(self, record: TaskRecord) -> TaskRecord:
        assert record.policy is not None
        assert record.plan is not None

        record.status = TaskStatus.EXECUTING
        record.touch()
        invocations = self.executor.execute(
            record.task_id,
            record.task,
            record.policy,
            context={"task": record.task, "task_id": record.task_id},
        )
        record.tool_invocations = invocations

        for invocation in invocations:
            if invocation.tool == "git_simulator" and invocation.success:
                record.branch_name = str(invocation.result.get("branch"))
                record.pr_url = str(invocation.result.get("pr_url"))
            if invocation.tool == "code_analyzer" and invocation.success:
                self.telemetry.emit(
                    record.task_id,
                    "security_check_completed",
                    {"passed": True, "simulated": True},
                )

        record.status = TaskStatus.REVIEWING
        record.touch()
        review = self.reviewer.review(
            record.policy,
            invocations,
            approval_granted=record.approval_granted or not record.policy.approval_required,
        )
        record.review = review

        productivity = estimate_productivity(risk_level=record.policy.risk_level.value)
        # Deterministic variation from task id for demo realism
        offset = int(record.task_id.replace("-", "")[:4], 16) % 7
        productivity.ai_assisted_minutes = max(6, productivity.ai_assisted_minutes - offset + 3)
        productivity.estimated_minutes_saved = max(
            0,
            productivity.estimated_manual_minutes - productivity.ai_assisted_minutes,
        )
        productivity.productivity_gain_percent = round(
            productivity.estimated_minutes_saved / productivity.estimated_manual_minutes * 100,
            1,
        )
        record.productivity = productivity

        if review.tests_passed and review.security_checks_passed and not review.policy_violations:
            record.status = TaskStatus.COMPLETED
            self.telemetry.emit(
                record.task_id,
                "task_completed",
                {"recommendation": review.recommendation},
            )
        else:
            record.status = TaskStatus.FAILED
            record.blocked_reason = "; ".join(review.unresolved_risks) or "review failed"
            self.telemetry.emit(
                record.task_id,
                "task_failed",
                {"reason": record.blocked_reason},
            )

        record.completed_at = datetime.now(UTC)
        record.report = self._build_report(record)
        self._persist(record)
        logger.info("Task %s finished with status %s", record.task_id, record.status)
        return record

    def _build_report(self, record: TaskRecord) -> dict[str, Any]:
        return {
            "task_id": record.task_id,
            "task": record.task,
            "status": record.status.value,
            "provider": record.provider,
            "plan": record.plan.model_dump(mode="json") if record.plan else None,
            "policy": record.policy.model_dump(mode="json") if record.policy else None,
            "review": record.review.model_dump(mode="json") if record.review else None,
            "branch": record.branch_name,
            "pull_request": record.pr_url,
            "blocked_reason": record.blocked_reason,
            "productivity": (
                record.productivity.model_dump(mode="json") if record.productivity else None
            ),
            "tool_invocations": [i.model_dump(mode="json") for i in record.tool_invocations],
            "change_summary": (
                "Proposed addition of health/build metadata endpoint with tests and simulated PR."
                if record.status == TaskStatus.COMPLETED
                else None
            ),
        }

    def _persist(self, record: TaskRecord) -> None:
        self._memory[record.task_id] = record
        policy = record.policy
        review = record.review
        productivity = record.productivity
        self.repository.upsert_task(
            {
                "task_id": record.task_id,
                "task": record.task,
                "status": record.status.value,
                "risk_level": policy.risk_level.value if policy else None,
                "provider": record.provider,
                "approval_required": int(bool(policy and policy.approval_required)),
                "approval_granted": int(record.approval_granted),
                "tests_passed": (None if review is None else int(review.tests_passed)),
                "security_passed": (None if review is None else int(review.security_checks_passed)),
                "blocked_reason": record.blocked_reason,
                "manual_minutes": (productivity.estimated_manual_minutes if productivity else None),
                "ai_minutes": productivity.ai_assisted_minutes if productivity else None,
                "branch_name": record.branch_name,
                "pr_url": record.pr_url,
                "report_json": json.dumps(record.report),
                "created_at": record.created_at.isoformat(),
                "updated_at": record.updated_at.isoformat(),
                "completed_at": record.completed_at.isoformat() if record.completed_at else None,
            }
        )

    def _row_to_record(self, row: dict[str, Any]) -> TaskRecord:
        report = json.loads(row["report_json"] or "{}")
        status = TaskStatus(row["status"])
        record = TaskRecord(
            task_id=row["task_id"],
            task=row["task"],
            status=status,
            provider=row.get("provider") or "mock",
            approval_granted=bool(row.get("approval_granted")),
            blocked_reason=row.get("blocked_reason"),
            branch_name=row.get("branch_name"),
            pr_url=row.get("pr_url"),
            report=report,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=(
                datetime.fromisoformat(row["completed_at"]) if row.get("completed_at") else None
            ),
        )
        return record
