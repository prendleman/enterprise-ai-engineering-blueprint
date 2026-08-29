"""Simulated file reader tool."""

from __future__ import annotations

from typing import Any

from app.tools.base import Tool


class FileReaderTool(Tool):
    name = "file_reader"

    def run(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        task = str(context.get("task", ""))
        return {
            "action": action or "inspect_routes",
            "files_reviewed": [
                "app/main.py",
                "app/api/routes.py",
                "app/api/schemas.py",
            ],
            "findings": [
                "FastAPI application entrypoint present",
                "No dedicated /health metadata payload yet"
                if "health" in task.lower()
                else "Existing API surface reviewed",
            ],
            "simulated": True,
        }
