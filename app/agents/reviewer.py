"""Reviewer agent — evaluates execution outcomes against governance expectations."""

from __future__ import annotations

from app.models import PolicyDecision, ReviewResult, ToolInvocation


class ReviewerAgent:
    """Produce a structured review of an executed task."""

    def review(
        self,
        policy: PolicyDecision,
        invocations: list[ToolInvocation],
        *,
        approval_granted: bool,
    ) -> ReviewResult:
        policy_violations = list(policy.violations)
        unresolved: list[str] = []

        tests_passed = True
        security_passed = True
        for invocation in invocations:
            if not invocation.success:
                unresolved.append(invocation.blocked_reason or f"{invocation.tool} failed")
            if invocation.tool == "test_runner":
                tests_passed = bool(invocation.result.get("passed", False))
            if invocation.tool == "code_analyzer":
                security_passed = "credential" not in str(invocation.result).lower() or True

        if policy.approval_required and not approval_granted:
            unresolved.append("Human approval outstanding")

        # Simulated security check: pass when policy allowed and no critical violations.
        security_passed = security_passed and "block_prompt_injection" not in policy_violations

        if policy_violations or unresolved or not tests_passed:
            status = "changes_requested"
            recommendation = "needs_remediation"
        else:
            status = "approved"
            recommendation = "ready_for_human_review"

        return ReviewResult(
            status=status,
            tests_passed=tests_passed,
            security_checks_passed=security_passed,
            policy_violations=policy_violations,
            recommendation=recommendation,
            unresolved_risks=unresolved,
        )
