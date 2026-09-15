"""Planner, executor, and reviewer agent roles."""

from __future__ import annotations

from app.models import (
    ReviewResult,
    RiskLevel,
    TaskPlan,
    TaskPlanStep,
    TaskRecord,
    ToolCallStatus,
)
from app.providers import AIProvider, parse_json_response
from app.tools import ToolRegistry


class PlannerAgent:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def plan(self, task: TaskRecord) -> TaskPlan:
        system = (
            "You are a planning agent for governed enterprise software engineering. "
            "Create a JSON plan with keys: summary, steps[{id,description,tool_name,risk,rationale}], "
            "overall_risk, estimated_manual_minutes, estimated_ai_minutes, notes. "
            "Risk must be one of LOW, MEDIUM, HIGH, CRITICAL."
        )
        user = f"Create a plan for title={task.title!r} description={task.description!r}"
        raw = self.provider.complete(system, user)
        data = parse_json_response(raw)
        steps = [
            TaskPlanStep(
                id=str(step.get("id", f"s{i}")),
                description=str(step.get("description", "step")),
                tool_name=step.get("tool_name"),
                risk=RiskLevel(str(step.get("risk", "MEDIUM")).upper()),
                rationale=str(step.get("rationale", "")),
            )
            for i, step in enumerate(data.get("steps", []), start=1)
        ]
        return TaskPlan(
            summary=str(data.get("summary", "Plan generated")),
            steps=steps,
            overall_risk=RiskLevel(str(data.get("overall_risk", "MEDIUM")).upper()),
            estimated_manual_minutes=int(data.get("estimated_manual_minutes", 60)),
            estimated_ai_minutes=int(data.get("estimated_ai_minutes", 20)),
            notes=[str(n) for n in data.get("notes", [])],
        )


class ExecutorAgent:
    def __init__(self, registry: ToolRegistry, *, block_critical: bool = True) -> None:
        self.registry = registry
        self.block_critical = block_critical

    def execute_plan(self, task: TaskRecord, *, approved_tools: set[str] | None = None) -> TaskRecord:
        approved_tools = approved_tools or set()
        if not task.plan:
            return task
        for step in task.plan.steps:
            if not step.tool_name:
                continue
            invocation = self.registry.invoke(
                step.tool_name,
                {"task_id": task.id, "step_id": step.id, "title": task.title},
                approved=step.tool_name in approved_tools or step.risk in {RiskLevel.LOW, RiskLevel.MEDIUM},
                block_critical=self.block_critical,
            )
            # Medium risk tools execute without human gate; high needs approval.
            if step.risk == RiskLevel.HIGH and step.tool_name not in approved_tools:
                invocation = self.registry.invoke(
                    step.tool_name,
                    {"task_id": task.id, "step_id": step.id, "title": task.title},
                    approved=False,
                    block_critical=self.block_critical,
                )
            task.tool_calls.append(invocation)
            if invocation.status == ToolCallStatus.BLOCKED:
                task.blocked_reason = task.blocked_reason or invocation.message
                break
            if invocation.status == ToolCallStatus.PENDING_APPROVAL:
                break
            if invocation.tool_name == "git.create_branch" and invocation.result:
                task.branch_name = str(invocation.result.get("branch"))
            if invocation.tool_name == "git.open_pr" and invocation.result:
                task.pr_url = str(invocation.result.get("pr_url"))
        return task


class ReviewerAgent:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    def review(self, task: TaskRecord) -> ReviewResult:
        if task.blocked_reason or any(c.status.value == "blocked" for c in task.tool_calls):
            return ReviewResult(
                approved=False,
                findings=["Execution blocked by policy."],
                security_pass=False,
                tests_pass=False,
                summary="Blocked tasks cannot be approved.",
            )
        system = (
            "You are a reviewer agent. Return JSON with approved, findings, "
            "security_pass, tests_pass, summary."
        )
        user = (
            f"Review task {task.title}. Tools={[c.tool_name for c in task.tool_calls]} "
            f"statuses={[c.status.value for c in task.tool_calls]}"
        )
        data = parse_json_response(self.provider.complete(system, user))
        return ReviewResult(
            approved=bool(data.get("approved", True)),
            findings=[str(f) for f in data.get("findings", [])],
            security_pass=bool(data.get("security_pass", True)),
            tests_pass=bool(data.get("tests_pass", True)),
            summary=str(data.get("summary", "Review complete")),
        )
