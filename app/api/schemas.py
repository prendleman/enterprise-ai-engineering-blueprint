"""API request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    task: str = Field(min_length=3, max_length=2000)
    auto_approve: bool = False


class TaskCreateResponse(BaseModel):
    task_id: str
    status: str
    message: str


class ApprovalResponse(BaseModel):
    task_id: str
    status: str
    approval_granted: bool


class TaskDetailResponse(BaseModel):
    task_id: str
    task: str
    status: str
    provider: str
    report: dict[str, Any]
    blocked_reason: str | None = None


class RootResponse(BaseModel):
    project: str
    status: str
    provider: str


class HealthResponse(BaseModel):
    status: str
    version: str
    provider: str
