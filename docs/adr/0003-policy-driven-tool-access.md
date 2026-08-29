# ADR 0003: Policy-Driven Tool Access

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Agents request tools. If tool availability is implicit in code, least privilege erodes over time and security reviews cannot reason about capability surface from configuration alone.

## Decision

Maintain an explicit tool registry in `config/tools.yaml`. The executor may only invoke tools that are enabled. Disabled tools (e.g., `shell`, `production_database`) are blocked at runtime and emit `tool_blocked` telemetry even if requested by a plan.

## Alternatives Considered

1. **Hard-coded tool list in executor** — drifts from documentation; opaque to auditors.
2. **Full unrestricted tool use inside a sandbox** — stronger isolation story, but still needs policy and is out of scope for this lightweight prototype.
3. **Per-task free-text permissions** — inconsistent and hard to test.

## Consequences

- Capability changes become config PRs reviewable by security CODEOWNERS.
- Tests can assert disabled tools never execute.
- Adding a new dangerous tool defaults to explicit enablement decisions.
