"""Human approval gate evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from app.models import RiskLevel
from app.settings import load_yaml


@dataclass(frozen=True)
class ApprovalRule:
    approval_required: bool
    execution_allowed: bool


class ApprovalService:
    """Determine whether a risk level requires human approval."""

    def __init__(self) -> None:
        rules = load_yaml("policies.yaml").get("approval_rules", {})
        self._rules: dict[RiskLevel, ApprovalRule] = {}
        for level in RiskLevel:
            raw = rules.get(level.value, {})
            self._rules[level] = ApprovalRule(
                approval_required=bool(raw.get("approval_required", False)),
                execution_allowed=bool(raw.get("execution_allowed", True)),
            )

    def rule_for(self, risk: RiskLevel) -> ApprovalRule:
        return self._rules[risk]

    def requires_approval(self, risk: RiskLevel) -> bool:
        return self._rules[risk].approval_required

    def execution_allowed(self, risk: RiskLevel) -> bool:
        return self._rules[risk].execution_allowed
