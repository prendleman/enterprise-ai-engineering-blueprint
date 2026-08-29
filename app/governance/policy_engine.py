"""Policy engine combining prompt guards, risk, tools, and approval rules."""

from __future__ import annotations

from app.governance.approvals import ApprovalService
from app.governance.risk import RiskEngine
from app.governance.tool_registry import ToolRegistry
from app.models import AgentPlan, PolicyDecision, RiskLevel
from app.security.prompt_guard import inspect_prompt


class PolicyEngine:
    """Evaluate whether a planned agent task may proceed."""

    def __init__(
        self,
        risk_engine: RiskEngine | None = None,
        tool_registry: ToolRegistry | None = None,
        approval_service: ApprovalService | None = None,
    ) -> None:
        self.risk_engine = risk_engine or RiskEngine()
        self.tool_registry = tool_registry or ToolRegistry()
        self.approval_service = approval_service or ApprovalService()

    def evaluate(self, task: str, plan: AgentPlan | None = None) -> PolicyDecision:
        """Run governance checks for a task and optional plan."""
        violations: list[str] = []
        reasons: list[str] = []

        guard = inspect_prompt(task)
        if not guard.safe:
            return PolicyDecision(
                allowed=False,
                risk_level=RiskLevel.CRITICAL,
                approval_required=True,
                execution_allowed=False,
                violations=["block_prompt_injection"],
                reasons=[guard.reason or "security policy violation"],
                allowed_tools=[],
            )

        tools = plan.tools_requested if plan else []
        risk = self.risk_engine.assess(task, tools)
        if plan and plan.estimated_risk:
            risk = max(risk, plan.estimated_risk, key=RiskEngine.score)

        allowed_tools, blocked_tools = self.tool_registry.filter_allowed(tools)
        if blocked_tools:
            violations.append("block_disabled_tools")
            reasons.append(f"Disabled tools requested: {', '.join(blocked_tools)}")

        approval_rule = self.approval_service.rule_for(risk)
        if risk == RiskLevel.CRITICAL or not approval_rule.execution_allowed:
            violations.append("block_critical_execution")
            reasons.append("Critical-risk actions are not executable in this blueprint")
            return PolicyDecision(
                allowed=False,
                risk_level=risk,
                approval_required=True,
                execution_allowed=False,
                violations=violations,
                reasons=reasons,
                allowed_tools=allowed_tools,
            )

        if blocked_tools and not allowed_tools:
            return PolicyDecision(
                allowed=False,
                risk_level=risk,
                approval_required=approval_rule.approval_required,
                execution_allowed=False,
                violations=violations,
                reasons=reasons,
                allowed_tools=[],
            )

        if approval_rule.approval_required:
            reasons.append("Human approval required for this risk level")

        return PolicyDecision(
            allowed=True,
            risk_level=risk,
            approval_required=approval_rule.approval_required,
            execution_allowed=approval_rule.execution_allowed,
            violations=violations,
            reasons=reasons,
            allowed_tools=allowed_tools or self.tool_registry.enabled_tools(),
        )
