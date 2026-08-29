"""Telemetry event persistence using SQLite."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.security.sanitization import sanitize_payload
from app.settings import ensure_data_dir, get_settings


@dataclass
class TelemetryEvent:
    id: int
    task_id: str
    event_type: str
    payload: dict[str, Any]
    created_at: str


class TelemetryRepository:
    """SQLite-backed telemetry store."""

    def __init__(self, db_path: Path | None = None) -> None:
        ensure_data_dir()
        self.db_path = db_path or get_settings().db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    risk_level TEXT,
                    provider TEXT,
                    approval_required INTEGER DEFAULT 0,
                    approval_granted INTEGER DEFAULT 0,
                    tests_passed INTEGER,
                    security_passed INTEGER,
                    blocked_reason TEXT,
                    manual_minutes INTEGER,
                    ai_minutes INTEGER,
                    branch_name TEXT,
                    pr_url TEXT,
                    report_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_events_task ON events(task_id);
                CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
                """
            )
            conn.commit()

    def add_event(
        self,
        task_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        clean = sanitize_payload(payload or {})
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO events (task_id, event_type, payload, created_at) VALUES (?, ?, ?, ?)",
                (
                    task_id,
                    event_type,
                    json.dumps(clean),
                    datetime.now(UTC).isoformat(),
                ),
            )

    def list_events(self, task_id: str | None = None, limit: int = 200) -> list[TelemetryEvent]:
        query = "SELECT id, task_id, event_type, payload, created_at FROM events"
        params: list[Any] = []
        if task_id:
            query += " WHERE task_id = ?"
            params.append(task_id)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [
            TelemetryEvent(
                id=row["id"],
                task_id=row["task_id"],
                event_type=row["event_type"],
                payload=json.loads(row["payload"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def upsert_task(self, record: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tasks (
                    task_id, task, status, risk_level, provider, approval_required,
                    approval_granted, tests_passed, security_passed, blocked_reason,
                    manual_minutes, ai_minutes, branch_name, pr_url, report_json,
                    created_at, updated_at, completed_at
                ) VALUES (
                    :task_id, :task, :status, :risk_level, :provider, :approval_required,
                    :approval_granted, :tests_passed, :security_passed, :blocked_reason,
                    :manual_minutes, :ai_minutes, :branch_name, :pr_url, :report_json,
                    :created_at, :updated_at, :completed_at
                )
                ON CONFLICT(task_id) DO UPDATE SET
                    task=excluded.task,
                    status=excluded.status,
                    risk_level=excluded.risk_level,
                    provider=excluded.provider,
                    approval_required=excluded.approval_required,
                    approval_granted=excluded.approval_granted,
                    tests_passed=excluded.tests_passed,
                    security_passed=excluded.security_passed,
                    blocked_reason=excluded.blocked_reason,
                    manual_minutes=excluded.manual_minutes,
                    ai_minutes=excluded.ai_minutes,
                    branch_name=excluded.branch_name,
                    pr_url=excluded.pr_url,
                    report_json=excluded.report_json,
                    updated_at=excluded.updated_at,
                    completed_at=excluded.completed_at
                """,
                record,
            )

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    def list_tasks(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def count_events_by_type(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT event_type, COUNT(*) AS cnt FROM events GROUP BY event_type"
            ).fetchall()
        return {row["event_type"]: int(row["cnt"]) for row in rows}
