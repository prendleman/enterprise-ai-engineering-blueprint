"""Engineering metrics calculations."""

from __future__ import annotations

from typing import Any

from app.models import ProductivityEstimate
from app.settings import get_settings
from app.telemetry.repository import TelemetryRepository


def estimate_productivity(
    *,
    risk_level: str,
    manual_minutes: int | None = None,
    ai_minutes: int | None = None,
) -> ProductivityEstimate:
    """Return a clearly labeled simulated productivity estimate.

    These values are illustrative model outputs for demo dashboards, not
    experimentally validated productivity research results.
    """
    settings = get_settings()
    if manual_minutes is not None:
        estimated_manual = manual_minutes
    else:
        risk_factor = {"low": 0.7, "medium": 1.0, "high": 1.4, "critical": 1.8}.get(risk_level, 1.0)
        estimated_manual = int(settings.default_manual_minutes * risk_factor)
    assisted = ai_minutes if ai_minutes is not None else max(8, int(estimated_manual * 0.24))
    saved = max(0, estimated_manual - assisted)
    gain = round((saved / estimated_manual) * 100, 1) if estimated_manual else 0.0
    return ProductivityEstimate(
        estimated_manual_minutes=estimated_manual,
        ai_assisted_minutes=assisted,
        estimated_minutes_saved=saved,
        productivity_gain_percent=gain,
    )


class MetricsCalculator:
    """Aggregate delivery, AI, governance, and productivity metrics."""

    def __init__(self, repository: TelemetryRepository | None = None) -> None:
        self.repository = repository or TelemetryRepository()

    def summarize(self) -> dict[str, Any]:
        tasks = self.repository.list_tasks(limit=10_000)
        events = self.repository.count_events_by_type()
        total = len(tasks)
        completed = [t for t in tasks if t["status"] == "completed"]
        failed = [t for t in tasks if t["status"] == "failed"]
        blocked = [t for t in tasks if t["status"] == "blocked"]
        awaiting = [t for t in tasks if t["status"] == "awaiting_approval"]

        tests_known = [t for t in tasks if t["tests_passed"] is not None]
        security_known = [t for t in tasks if t["security_passed"] is not None]
        approvals_required = [t for t in tasks if t["approval_required"]]
        approvals_granted = [t for t in tasks if t["approval_granted"]]

        manual_total = sum(int(t["manual_minutes"] or 0) for t in completed)
        ai_total = sum(int(t["ai_minutes"] or 0) for t in completed)
        saved_total = max(0, manual_total - ai_total)

        high_risk = [
            t for t in tasks if (t.get("risk_level") or "").lower() in {"high", "critical"}
        ]

        completion_rate = (len(completed) / total * 100) if total else 0.0
        test_pass_rate = (
            sum(1 for t in tests_known if t["tests_passed"]) / len(tests_known) * 100
            if tests_known
            else 0.0
        )
        security_pass_rate = (
            sum(1 for t in security_known if t["security_passed"]) / len(security_known) * 100
            if security_known
            else 0.0
        )
        tool_invoked = events.get("tool_invoked", 0)
        tool_blocked = events.get("tool_blocked", 0)
        tool_total = tool_invoked + tool_blocked
        tool_success_rate = (tool_invoked / tool_total * 100) if tool_total else 0.0

        return {
            "delivery": {
                "tasks_total": total,
                "tasks_completed": len(completed),
                "completion_rate": round(completion_rate, 1),
                "average_completion_minutes": round(
                    (sum(int(t["ai_minutes"] or 0) for t in completed) / len(completed))
                    if completed
                    else 0.0,
                    1,
                ),
                "simulated_pr_cycle_hours": 4.2,
                "test_pass_rate": round(test_pass_rate, 1),
                "security_pass_rate": round(security_pass_rate, 1),
            },
            "ai": {
                "plan_success_rate": round(
                    ((len(completed) + len(awaiting)) / total * 100 if total else 0.0),
                    1,
                ),
                "tool_call_success_rate": round(tool_success_rate, 1),
                "blocked_tool_attempts": tool_blocked,
                "tasks_requiring_human_approval": len(approvals_required),
                "agent_failure_rate": round((len(failed) / total * 100) if total else 0.0, 1),
            },
            "governance": {
                "policy_violations": events.get("task_failed", 0) + len(blocked),
                "prevented_critical_actions": len(blocked),
                "approvals_requested": events.get("approval_requested", 0),
                "approvals_granted": len(approvals_granted),
                "high_risk_task_percentage": round(
                    (len(high_risk) / total * 100) if total else 0.0,
                    1,
                ),
            },
            "productivity": {
                "label": "simulated_estimate",
                "estimated_manual_minutes": manual_total,
                "ai_assisted_minutes": ai_total,
                "estimated_minutes_saved": saved_total,
                "estimated_hours_saved": round(saved_total / 60, 1),
                "productivity_gain_percent": round(
                    (saved_total / manual_total * 100) if manual_total else 0.0,
                    1,
                ),
            },
            "outcomes": {
                "successful": len(completed),
                "failed": len(failed),
                "blocked": len(blocked),
                "approval_required": len(awaiting),
            },
            "events": events,
        }
