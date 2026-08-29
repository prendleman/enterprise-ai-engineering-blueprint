"""FastAPI route definitions."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app import __version__
from app.api.schemas import (
    ApprovalResponse,
    HealthResponse,
    RootResponse,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskDetailResponse,
)
from app.services.task_service import TaskService
from app.settings import provider_name
from app.telemetry.metrics import MetricsCalculator

router = APIRouter()


def _service(request: Request) -> TaskService:
    return request.app.state.task_service  # type: ignore[no-any-return]


@router.get("/", response_model=RootResponse)
def root() -> RootResponse:
    return RootResponse(
        project="Enterprise AI Engineering Blueprint",
        status="running",
        provider=provider_name(),
    )


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=__version__,
        provider=provider_name(),
    )


@router.post("/tasks", response_model=TaskCreateResponse)
def create_task(payload: TaskCreateRequest, request: Request) -> TaskCreateResponse:
    service = _service(request)
    record = service.create_task(payload.task, auto_approve=payload.auto_approve)
    message = {
        "completed": "Task completed through governed agent workflow",
        "awaiting_approval": "Human approval required before execution",
        "blocked": record.blocked_reason or "Blocked by security policy",
        "failed": record.blocked_reason or "Task failed review",
    }.get(record.status.value, f"Task status: {record.status.value}")
    return TaskCreateResponse(
        task_id=record.task_id,
        status=record.status.value,
        message=message,
    )


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str, request: Request) -> TaskDetailResponse:
    service = _service(request)
    try:
        record = service.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    return TaskDetailResponse(
        task_id=record.task_id,
        task=record.task,
        status=record.status.value,
        provider=record.provider,
        report=record.report,
        blocked_reason=record.blocked_reason,
    )


@router.post("/tasks/{task_id}/approve", response_model=ApprovalResponse)
def approve_task(task_id: str, request: Request) -> ApprovalResponse:
    service = _service(request)
    try:
        record = service.approve_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApprovalResponse(
        task_id=record.task_id,
        status=record.status.value,
        approval_granted=record.approval_granted,
    )


@router.get("/tasks/{task_id}/events")
def task_events(task_id: str, request: Request) -> dict[str, object]:
    service = _service(request)
    try:
        service.get_task(task_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Task not found") from exc
    return {"task_id": task_id, "events": service.list_events(task_id)}


@router.get("/metrics")
def metrics(request: Request) -> dict[str, object]:
    repo = request.app.state.task_service.repository
    return MetricsCalculator(repo).summarize()
