"""Policy-controlled tool registry with least-privilege allowlist."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from app.models import RiskLevel, ToolCallStatus, ToolInvocation, new_id, utc_now

ToolHandler = Callable[[dict[str, Any]], dict[str, Any]]


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    risk: RiskLevel
    handler: ToolHandler
    allowed: bool = True


class PolicyError(Exception):
    def __init__(self, message: str, status: ToolCallStatus) -> None:
        super().__init__(message)
        self.status = status


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, spec: ToolSpec) -> None:
        self._tools[spec.name] = spec

    def get(self, name: str) -> ToolSpec | None:
        return self._tools.get(name)

    def list_tools(self) -> list[dict[str, str]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "risk": t.risk.value,
                "allowed": str(t.allowed),
            }
            for t in self._tools.values()
        ]

    def invoke(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        approved: bool = False,
        block_critical: bool = True,
    ) -> ToolInvocation:
        spec = self._tools.get(name)
        if spec is None or not spec.allowed:
            return ToolInvocation(
                id=new_id("tool"),
                tool_name=name,
                arguments=arguments,
                risk=RiskLevel.CRITICAL,
                status=ToolCallStatus.BLOCKED,
                message="Tool not on allowlist",
            )

        if spec.risk == RiskLevel.CRITICAL and block_critical:
            return ToolInvocation(
                id=new_id("tool"),
                tool_name=name,
                arguments=arguments,
                risk=spec.risk,
                status=ToolCallStatus.BLOCKED,
                message="CRITICAL tools are blocked by default policy",
            )

        if spec.risk == RiskLevel.HIGH and not approved:
            return ToolInvocation(
                id=new_id("tool"),
                tool_name=name,
                arguments=arguments,
                risk=spec.risk,
                status=ToolCallStatus.PENDING_APPROVAL,
                message="Human approval required before execution",
            )

        try:
            result = spec.handler(arguments)
            return ToolInvocation(
                id=new_id("tool"),
                tool_name=name,
                arguments=arguments,
                risk=spec.risk,
                status=ToolCallStatus.EXECUTED,
                result=result,
                message="Executed under policy",
                created_at=utc_now(),
            )
        except Exception as exc:  # noqa: BLE001 - surface tool failures to audit trail
            return ToolInvocation(
                id=new_id("tool"),
                tool_name=name,
                arguments=arguments,
                risk=spec.risk,
                status=ToolCallStatus.FAILED,
                message=str(exc),
            )


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    def create_branch(args: dict[str, Any]) -> dict[str, Any]:
        name = args.get("name") or "feature/agent-change"
        return {"branch": name, "simulation": True}

    def apply_patch(args: dict[str, Any]) -> dict[str, Any]:
        return {
            "files_changed": args.get("files", ["app/api.py"]),
            "summary": args.get("summary", "Applied governed patch"),
            "simulation": True,
        }

    def run_checks(args: dict[str, Any]) -> dict[str, Any]:
        return {
            "tests_passed": True,
            "security_passed": True,
            "lint_passed": True,
            "suite": args.get("suite", "default"),
            "simulation": True,
        }

    def open_pr(args: dict[str, Any]) -> dict[str, Any]:
        branch = args.get("branch", "feature/agent-change")
        return {
            "pr_url": f"https://github.example.local/org/app/pull/sim-{branch.replace('/', '-')}",
            "title": args.get("title", "Governed agent change"),
            "simulation": True,
        }

    def dump_env(_args: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("secrets.dump_env must never execute")

    def disable_security(_args: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("security.disable_checks must never execute")

    def evaluate_policy(args: dict[str, Any]) -> dict[str, Any]:
        return {"decision": "deny", "reason": args.get("reason", "policy violation"), "simulation": True}

    registry.register(
        ToolSpec("git.create_branch", "Create a feature branch (simulated)", RiskLevel.LOW, create_branch)
    )
    registry.register(
        ToolSpec("code.apply_patch", "Apply a code patch (simulated)", RiskLevel.MEDIUM, apply_patch)
    )
    registry.register(ToolSpec("ci.run_checks", "Run tests/security checks", RiskLevel.LOW, run_checks))
    registry.register(ToolSpec("git.open_pr", "Open a pull request (simulated)", RiskLevel.MEDIUM, open_pr))
    registry.register(
        ToolSpec("policy.evaluate", "Evaluate request against policy", RiskLevel.LOW, evaluate_policy)
    )
    registry.register(
        ToolSpec(
            "secrets.dump_env",
            "Dump environment variables",
            RiskLevel.CRITICAL,
            dump_env,
            allowed=True,
        )
    )
    registry.register(
        ToolSpec(
            "security.disable_checks",
            "Disable security checks",
            RiskLevel.CRITICAL,
            disable_security,
            allowed=True,
        )
    )
    return registry
