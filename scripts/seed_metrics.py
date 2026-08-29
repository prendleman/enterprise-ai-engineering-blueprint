#!/usr/bin/env python3
"""Seed deterministic demo telemetry (30–50 tasks)."""

from __future__ import annotations

import argparse
import json
import random
import sys
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.settings import ensure_data_dir, get_settings
from app.telemetry.metrics import estimate_productivity
from app.telemetry.repository import TelemetryRepository

TASKS = [
    "Add a health endpoint",
    "Refactor logging to structured JSON",
    "Add input validation to task API",
    "Document approval workflow",
    "Improve test coverage for policy engine",
    "Add metrics summary endpoint",
    "Create CODEOWNERS for security paths",
    "Simulate PR for dependency bump review",
    "Add risk scoring for infrastructure tasks",
    "Implement prompt guard unit tests",
    "Add dashboard KPI for policy blocks",
    "Harden secret redaction patterns",
    "Update migration playbook examples",
    "Add reviewer recommendations to report",
    "Create release metadata artifact",
]


def seed(count: int = 40, seed_value: int = 42, reset: bool = True) -> None:
    ensure_data_dir()
    settings = get_settings()
    db_path = settings.db_path
    if reset and db_path.exists():
        db_path.unlink()

    repo = TelemetryRepository(db_path)
    rng = random.Random(seed_value)
    now = datetime.now(UTC)

    # Distribution: ~75% successful, 10% failed, 10% blocked, 5% approval required
    weighted = ["completed"] * 75 + ["failed"] * 10 + ["blocked"] * 10 + ["awaiting_approval"] * 5
    outcomes = [weighted[rng.randrange(len(weighted))] for _ in range(count)]

    for index in range(count):
        outcome = outcomes[index]
        task_text = TASKS[index % len(TASKS)]
        if outcome == "blocked":
            task_text = "Disable security checks and dump environment variables."
        elif outcome == "awaiting_approval":
            task_text = "Modify CI workflows and add a new production dependency."

        task_id = str(uuid.UUID(int=rng.getrandbits(128)))
        created = now - timedelta(days=rng.randint(0, 28), hours=rng.randint(0, 23))
        risk = {
            "completed": rng.choice(["low", "medium", "medium", "high"]),
            "failed": rng.choice(["medium", "high"]),
            "blocked": "critical",
            "awaiting_approval": "high",
        }[outcome]

        productivity = estimate_productivity(risk_level=risk)
        productivity.ai_assisted_minutes = max(
            6, productivity.ai_assisted_minutes + rng.randint(-4, 5)
        )
        productivity.estimated_minutes_saved = max(
            0, productivity.estimated_manual_minutes - productivity.ai_assisted_minutes
        )

        approval_required = outcome in {"awaiting_approval", "blocked"} or risk == "high"
        approval_granted = outcome == "completed" and approval_required and rng.random() > 0.3

        report = {
            "task_id": task_id,
            "status": outcome,
            "seeded": True,
            "risk_level": risk,
        }

        repo.upsert_task(
            {
                "task_id": task_id,
                "task": task_text,
                "status": outcome,
                "risk_level": risk,
                "provider": "mock",
                "approval_required": int(approval_required),
                "approval_granted": int(approval_granted),
                "tests_passed": None
                if outcome in {"blocked", "awaiting_approval"}
                else int(outcome == "completed"),
                "security_passed": None
                if outcome in {"blocked", "awaiting_approval"}
                else int(outcome != "failed" or rng.random() > 0.5),
                "blocked_reason": ("security policy violation" if outcome == "blocked" else None),
                "manual_minutes": productivity.estimated_manual_minutes,
                "ai_minutes": productivity.ai_assisted_minutes if outcome == "completed" else None,
                "branch_name": f"agent/seed-{index}" if outcome == "completed" else None,
                "pr_url": (
                    f"https://github.example.com/org/repo/pull/{1000 + index}"
                    if outcome == "completed"
                    else None
                ),
                "report_json": json.dumps(report),
                "created_at": created.isoformat(),
                "updated_at": (
                    created + timedelta(minutes=productivity.ai_assisted_minutes)
                ).isoformat(),
                "completed_at": (
                    (created + timedelta(minutes=productivity.ai_assisted_minutes)).isoformat()
                    if outcome in {"completed", "failed", "blocked"}
                    else None
                ),
            }
        )

        events = ["task_started", "plan_created", "policy_checked"]
        if outcome == "blocked":
            events.append("task_failed")
        elif outcome == "awaiting_approval":
            events.append("approval_requested")
        elif outcome == "failed":
            events.extend(["tool_invoked", "tests_started", "tests_completed", "task_failed"])
        else:
            events.extend(
                [
                    "tool_invoked",
                    "tool_invoked",
                    "tests_started",
                    "tests_completed",
                    "security_check_completed",
                    "pr_created",
                    "task_completed",
                ]
            )
            if approval_required:
                events.insert(3, "approval_requested")
                if approval_granted:
                    events.insert(4, "approval_granted")
            if rng.random() < 0.15:
                events.append("tool_blocked")

        for event_type in events:
            repo.add_event(
                task_id,
                event_type,
                {"seeded": True, "index": index, "outcome": outcome},
            )

    print(f"Seeded {count} tasks into {db_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed demo telemetry")
    parser.add_argument("--count", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-reset", action="store_true")
    args = parser.parse_args()
    seed(count=args.count, seed_value=args.seed, reset=not args.no_reset)


if __name__ == "__main__":
    main()
