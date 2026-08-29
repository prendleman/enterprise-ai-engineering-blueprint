# ADR 0002: Human Approval Gates

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

High-risk agent actions (CI modifications, dependency introduction, infrastructure changes) can create systemic blast radius. Autonomous execution without accountable human oversight is unacceptable for enterprise engineering platforms.

## Decision

Encode risk-based approval rules in `config/policies.yaml`. High-risk tasks transition to `awaiting_approval` and expose `POST /tasks/{id}/approve`. Critical-risk tasks require approval conceptually but are configured with `execution_allowed: false` in this blueprint.

## Alternatives Considered

1. **Approve every task** — excessive friction; encourages shadow bypasses.
2. **Approve nothing; rely on PR review only** — too late for dangerous tool invocations.
3. **Manager email approvals** — not machine-enforceable or auditable in-flow.

## Consequences

- Policy and API enforce pause/resume semantics.
- Telemetry captures `approval_requested` and `approval_granted`.
- Organizations must still configure GitHub rulesets so merges remain human-gated.
- Approval UX is intentionally minimal in the prototype (API-level).
