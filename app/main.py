"""FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.logging_config import configure_logging
from app.services.task_service import TaskService
from app.settings import ensure_data_dir, get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    ensure_data_dir()
    # Allow tests to inject a TaskService before startup.
    if not getattr(app.state, "task_service", None):
        app.state.task_service = TaskService()
    yield


app = FastAPI(
    title="Enterprise AI Engineering Blueprint",
    description=(
        "Reference architecture for governed enterprise adoption of agentic AI "
        "across software engineering workflows."
    ),
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)
