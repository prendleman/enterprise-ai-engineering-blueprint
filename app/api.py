"""FastAPI surface for task intake, status, approvals, and events."""

from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.models import (
    ApprovalDecision,
    HealthResponse,
    MetricsSnapshot,
    TaskCreate,
    TaskRecord,
    utc_now,
)
from app.orchestrator import Orchestrator
from app.telemetry import TelemetryStore
from app.tools import build_default_registry


@lru_cache
def get_orchestrator() -> Orchestrator:
    settings = get_settings()
    store = TelemetryStore(settings.db_path)
    return Orchestrator(store=store, block_critical=settings.block_critical)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=__version__)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok",
            app=settings.app_name,
            version=settings.app_version,
            build_sha=settings.build_sha,
            provider=settings.ai_provider,
            timestamp=utc_now(),
        )

    @app.post("/tasks", response_model=TaskRecord)
    def create_task(payload: TaskCreate) -> TaskRecord:
        return get_orchestrator().submit(payload)

    @app.get("/tasks", response_model=list[TaskRecord])
    def list_tasks() -> list[TaskRecord]:
        return get_orchestrator().list_tasks()

    @app.get("/tasks/{task_id}", response_model=TaskRecord)
    def get_task(task_id: str) -> TaskRecord:
        try:
            return get_orchestrator().get(task_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Task not found") from exc

    @app.post("/tasks/{task_id}/approvals/{approval_id}", response_model=TaskRecord)
    def decide(task_id: str, approval_id: str, decision: ApprovalDecision) -> TaskRecord:
        orch = get_orchestrator()
        try:
            return orch.decide_approval(task_id, approval_id, decision)
        except (KeyError, StopIteration) as exc:
            raise HTTPException(status_code=404, detail="Task or approval not found") from exc

    @app.get("/events/{task_id}")
    def events(task_id: str) -> list[dict[str, object]]:
        try:
            task = get_orchestrator().get(task_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Task not found") from exc
        return task.events

    @app.get("/metrics", response_model=MetricsSnapshot)
    def metrics() -> MetricsSnapshot:
        return get_orchestrator().store.metrics()

    @app.get("/tools")
    def tools() -> list[dict[str, str]]:
        return build_default_registry().list_tools()

    return app


app = create_app()
