"""Telemetry service facade."""

from __future__ import annotations

from typing import Any

from app.telemetry.repository import TelemetryRepository


class TelemetryService:
    """Emit and query engineering telemetry events."""

    def __init__(self, repository: TelemetryRepository | None = None) -> None:
        self.repository = repository or TelemetryRepository()

    def emit(self, task_id: str, event_type: str, payload: dict[str, Any] | None = None) -> None:
        self.repository.add_event(task_id, event_type, payload)

    def events_for(self, task_id: str) -> list[dict[str, Any]]:
        return [
            {
                "id": event.id,
                "task_id": event.task_id,
                "event_type": event.event_type,
                "payload": event.payload,
                "created_at": event.created_at,
            }
            for event in self.repository.list_events(task_id=task_id)
        ]
