"""Engineering telemetry store backed by DuckDB."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import duckdb

from app.models import MetricsSnapshot, TaskRecord, TaskStatus, ToolCallStatus, utc_now


class TelemetryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = duckdb.connect(str(self.db_path))
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
              id VARCHAR PRIMARY KEY,
              title VARCHAR,
              status VARCHAR,
              overall_risk VARCHAR,
              created_at TIMESTAMP,
              completed_at TIMESTAMP,
              manual_minutes INTEGER,
              ai_minutes INTEGER,
              payload JSON
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
              id VARCHAR,
              task_id VARCHAR,
              event_type VARCHAR,
              created_at TIMESTAMP,
              payload JSON
            )
            """
        )
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tool_calls (
              id VARCHAR,
              task_id VARCHAR,
              tool_name VARCHAR,
              risk VARCHAR,
              status VARCHAR,
              created_at TIMESTAMP
            )
            """
        )

    def upsert_task(self, task: TaskRecord) -> None:
        self._conn.execute("DELETE FROM tasks WHERE id = ?", [task.id])
        self._conn.execute(
            """
            INSERT INTO tasks
            (id, title, status, overall_risk, created_at, completed_at, manual_minutes, ai_minutes, payload)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                task.id,
                task.title,
                task.status.value,
                task.plan.overall_risk.value if task.plan else None,
                task.created_at,
                task.completed_at,
                task.plan.estimated_manual_minutes if task.plan else None,
                task.plan.estimated_ai_minutes if task.plan else None,
                task.model_dump_json(),
            ],
        )
        self._conn.execute("DELETE FROM tool_calls WHERE task_id = ?", [task.id])
        for call in task.tool_calls:
            self._conn.execute(
                """
                INSERT INTO tool_calls (id, task_id, tool_name, risk, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [call.id, task.id, call.tool_name, call.risk.value, call.status.value, call.created_at],
            )

    def record_event(self, task_id: str, event_type: str, payload: dict[str, Any]) -> None:
        event_id = f"evt_{task_id}_{event_type}_{utc_now().timestamp()}"
        self._conn.execute(
            """
            INSERT INTO events (id, task_id, event_type, created_at, payload)
            VALUES (?, ?, ?, ?, ?)
            """,
            [event_id, task_id, event_type, utc_now(), json.dumps(payload)],
        )

    def metrics(self) -> MetricsSnapshot:
        tasks = self._conn.execute(
            "SELECT status, created_at, completed_at, manual_minutes, ai_minutes, overall_risk FROM tasks"
        ).fetchall()
        tool_rows = self._conn.execute("SELECT status FROM tool_calls").fetchall()
        approval_sql = (
            "SELECT event_type FROM events "
            "WHERE event_type IN ('approval_granted','approval_denied','approval_pending')"
        )
        approval_rows = self._conn.execute(approval_sql).fetchall()

        total = len(tasks)
        completed = sum(1 for t in tasks if t[0] == TaskStatus.COMPLETED.value)
        blocked = sum(1 for t in tasks if t[0] == TaskStatus.BLOCKED.value)
        durations: list[float] = []
        manual = 0.0
        ai = 0.0
        high_risk = 0
        for _status, created, completed_at, man, ai_m, risk in tasks:
            if completed_at and created:
                durations.append((completed_at - created).total_seconds())
            manual += float(man or 0)
            ai += float(ai_m or 0)
            if risk in {"HIGH", "CRITICAL"}:
                high_risk += 1

        tool_total = len(tool_rows) or 1
        executed = sum(1 for r in tool_rows if r[0] == ToolCallStatus.EXECUTED.value)
        blocked_tools = sum(1 for r in tool_rows if r[0] == ToolCallStatus.BLOCKED.value)
        granted = sum(1 for r in approval_rows if r[0] == "approval_granted")
        denied = sum(1 for r in approval_rows if r[0] == "approval_denied")
        pending = sum(1 for r in approval_rows if r[0] == "approval_pending")

        review_rows = self._conn.execute("SELECT payload FROM tasks").fetchall()
        security_pass = 0
        tests_pass = 0
        reviewed = 0
        for (payload,) in review_rows:
            if not payload:
                continue
            data = json.loads(payload) if isinstance(payload, str) else payload
            review = data.get("review") if isinstance(data, dict) else None
            if not review:
                continue
            reviewed += 1
            security_pass += int(bool(review.get("security_pass")))
            tests_pass += int(bool(review.get("tests_pass")))

        return MetricsSnapshot(
            tasks_total=total,
            tasks_completed=completed,
            tasks_blocked=blocked,
            avg_completion_seconds=(sum(durations) / len(durations)) if durations else 0.0,
            simulated_pr_cycle_minutes=45.0 if completed else 0.0,
            test_pass_rate=(tests_pass / reviewed) if reviewed else 0.0,
            security_pass_rate=(security_pass / reviewed) if reviewed else 0.0,
            tool_call_success_rate=executed / tool_total,
            blocked_tool_attempts=blocked_tools,
            approvals_pending=pending,
            approvals_granted=granted,
            approvals_denied=denied,
            policy_violations=blocked_tools + denied,
            high_risk_percentage=(high_risk / total * 100.0) if total else 0.0,
            simulated_manual_minutes=manual,
            simulated_ai_minutes=ai,
            simulated_minutes_saved=max(manual - ai, 0.0),
        )

    def close(self) -> None:
        self._conn.close()
