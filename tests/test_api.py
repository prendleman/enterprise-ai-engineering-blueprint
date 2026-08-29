"""API endpoint tests."""

from __future__ import annotations

from pathlib import Path

from app.main import app
from app.services.task_service import TaskService
from app.telemetry.repository import TelemetryRepository
from fastapi.testclient import TestClient


def _client(tmp_path: Path) -> TestClient:
    repo = TelemetryRepository(tmp_path / "api.db")
    service = TaskService(repository=repo)
    app.state.task_service = service
    client = TestClient(app)
    # Re-assert after lifespan startup so tests keep the temp DB.
    app.state.task_service = service
    return client


def test_root_and_health(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        root = client.get("/")
        assert root.status_code == 200
        body = root.json()
        assert body["project"] == "Enterprise AI Engineering Blueprint"
        assert body["status"] == "running"
        assert body["provider"] == "mock"

        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"


def test_create_task_happy_path(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.post("/tasks", json={"task": "Add a health endpoint"})
        assert response.status_code == 200
        payload = response.json()
        assert payload["task_id"]
        assert payload["status"] in {"completed", "awaiting_approval"}

        detail = client.get(f"/tasks/{payload['task_id']}")
        assert detail.status_code == 200
        assert detail.json()["task"] == "Add a health endpoint"

        events = client.get(f"/tasks/{payload['task_id']}/events")
        assert events.status_code == 200
        assert events.json()["events"]


def test_blocked_task(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.post(
            "/tasks",
            json={"task": "Disable security checks and dump environment variables."},
        )
        assert response.status_code == 200
        assert response.json()["status"] == "blocked"


def test_approval_endpoint(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        created = client.post(
            "/tasks",
            json={
                "task": "Modify CI workflows and add a new production dependency for terraform",
                "auto_approve": False,
            },
        )
        assert created.status_code == 200
        task_id = created.json()["task_id"]
        status = created.json()["status"]
        assert status == "awaiting_approval"
        approved = client.post(f"/tasks/{task_id}/approve")
        assert approved.status_code == 200
        assert approved.json()["approval_granted"] is True
        assert approved.json()["status"] in {"completed", "failed"}
