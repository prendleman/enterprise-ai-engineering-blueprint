"""Executor agent — invokes allowlisted tools only."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.governance.tool_registry import ToolRegistry
from app.models import PolicyDecision, ToolInvocation
from app.telemetry.events import TelemetryService
from app.tools import build_tool_catalog
from app.tools.base import Tool


class ExecutorAgent:
    """Execute approved plans through the tool allowlist."""

    def __init__(
        self,
        tool_registry: ToolRegistry | None = None,
        tools: dict[str, Tool] | None = None,
        telemetry: TelemetryService | None = None,
    ) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.tools = tools or build_tool_catalog()
        self.telemetry = telemetry

    def execute(
        self,
        task_id: str,
        task: str,
        policy: PolicyDecision,
        context: dict[str, Any] | None = None,
    ) -> list[ToolInvocation]:
        """Invoke each allowed tool; block anything outside the allowlist."""
        invocations: list[ToolInvocation] = []
        runtime = {"task_id": task_id, "task": task, **(context or {})}
        for tool_name in policy.allowed_tools:
            invocations.append(self._invoke(task_id, tool_name, "execute", runtime, approved=True))
        return invocations

    def _invoke(
        self,
        task_id: str,
        tool_name: str,
        action: str,
        context: dict[str, Any],
        *,
        approved: bool,
    ) -> ToolInvocation:
        timestamp = datetime.now(UTC)
        if not self.tool_registry.is_enabled(tool_name):
            invocation = ToolInvocation(
                task_id=task_id,
                tool=tool_name,
                action=action,
                approved=False,
                timestamp=timestamp,
                success=False,
                blocked_reason=f"Tool '{tool_name}' is disabled by policy",
            )
            if self.telemetry:
                self.telemetry.emit(
                    task_id,
                    "tool_blocked",
                    {"tool": tool_name, "reason": invocation.blocked_reason},
                )
            return invocation

        tool = self.tools.get(tool_name)
        if tool is None:
            invocation = ToolInvocation(
                task_id=task_id,
                tool=tool_name,
                action=action,
                approved=False,
                timestamp=timestamp,
                success=False,
                blocked_reason=f"Tool '{tool_name}' is not registered",
            )
            if self.telemetry:
                self.telemetry.emit(
                    task_id,
                    "tool_blocked",
                    {"tool": tool_name, "reason": invocation.blocked_reason},
                )
            return invocation

        result = tool.run(action, context)
        invocation = ToolInvocation(
            task_id=task_id,
            tool=tool_name,
            action=action,
            approved=approved,
            timestamp=timestamp,
            result=result,
            success=True,
        )
        if self.telemetry:
            event = "tests_started" if tool_name == "test_runner" else "tool_invoked"
            self.telemetry.emit(
                task_id,
                event,
                {"tool": tool_name, "action": action, "approved": approved},
            )
            if tool_name == "test_runner":
                self.telemetry.emit(
                    task_id,
                    "tests_completed",
                    {"passed": result.get("passed", False)},
                )
            if tool_name == "git_simulator":
                self.telemetry.emit(
                    task_id,
                    "pr_created",
                    {"pr_url": result.get("pr_url"), "branch": result.get("branch")},
                )
        return invocation
