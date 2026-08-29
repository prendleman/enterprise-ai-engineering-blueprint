"""Simulated static code analyzer."""

from __future__ import annotations

from typing import Any

from app.tools.base import Tool


class CodeAnalyzerTool(Tool):
    name = "code_analyzer"

    def run(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "action": action or "analyze",
            "complexity": "low",
            "suggested_changes": [
                "Add GET /health returning status and build metadata",
                "Include provider and version fields",
                "Add API schema and pytest coverage",
            ],
            "security_notes": ["No credential handling required for health endpoint"],
            "simulated": True,
        }
