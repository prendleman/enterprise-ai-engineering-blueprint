"""Telemetry and metrics tests."""

from __future__ import annotations

from pathlib import Path

from app.telemetry.metrics import MetricsCalculator, estimate_productivity
from app.telemetry.repository import TelemetryRepository


def test_telemetry_creation(tmp_path: Path) -> None:
    repo = TelemetryRepository(tmp_path / "metrics.db")
    repo.add_event("t1", "task_started", {"task": "demo"})
    repo.add_event("t1", "tool_invoked", {"api_key": "sk-should-redact-value"})
    events = repo.list_events("t1")
    assert len(events) == 2
    assert events[0].event_type in {"task_started", "tool_invoked"}
    # newest first
    payloads = [event.payload for event in events]
    assert any("[REDACTED]" in str(payload) for payload in payloads)


def test_metric_calculations(tmp_path: Path) -> None:
    repo = TelemetryRepository(tmp_path / "metrics.db")
    repo.upsert_task(
        {
            "task_id": "a",
            "task": "one",
            "status": "completed",
            "risk_level": "low",
            "provider": "mock",
            "approval_required": 0,
            "approval_granted": 0,
            "tests_passed": 1,
            "security_passed": 1,
            "blocked_reason": None,
            "manual_minutes": 75,
            "ai_minutes": 18,
            "branch_name": "b",
            "pr_url": "http://example",
            "report_json": "{}",
            "created_at": "2026-01-01T00:00:00+00:00",
            "updated_at": "2026-01-01T00:20:00+00:00",
            "completed_at": "2026-01-01T00:20:00+00:00",
        }
    )
    repo.upsert_task(
        {
            "task_id": "b",
            "task": "two",
            "status": "blocked",
            "risk_level": "critical",
            "provider": "mock",
            "approval_required": 1,
            "approval_granted": 0,
            "tests_passed": None,
            "security_passed": None,
            "blocked_reason": "security policy violation",
            "manual_minutes": None,
            "ai_minutes": None,
            "branch_name": None,
            "pr_url": None,
            "report_json": "{}",
            "created_at": "2026-01-02T00:00:00+00:00",
            "updated_at": "2026-01-02T00:01:00+00:00",
            "completed_at": "2026-01-02T00:01:00+00:00",
        }
    )
    repo.add_event("a", "tool_invoked", {})
    repo.add_event("b", "tool_blocked", {})
    summary = MetricsCalculator(repo).summarize()
    assert summary["delivery"]["tasks_completed"] == 1
    assert summary["governance"]["prevented_critical_actions"] == 1
    assert summary["productivity"]["label"] == "simulated_estimate"
    assert summary["productivity"]["estimated_minutes_saved"] == 57


def test_productivity_estimate_label() -> None:
    estimate = estimate_productivity(risk_level="low", manual_minutes=100, ai_minutes=25)
    assert estimate.label == "simulated_estimate"
    assert estimate.estimated_minutes_saved == 75
    assert estimate.productivity_gain_percent == 75.0
