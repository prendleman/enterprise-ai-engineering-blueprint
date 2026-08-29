"""Simulated test runner tool."""

from __future__ import annotations

from typing import Any

from app.tools.base import Tool


class TestRunnerTool(Tool):
    name = "test_runner"

    def run(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        force_fail = bool(context.get("force_test_failure", False))
        passed = not force_fail
        return {
            "action": action or "run_tests",
            "passed": passed,
            "tests_run": 12,
            "failures": 0 if passed else 1,
            "coverage_percent": 86 if passed else 71,
            "simulated": True,
        }
