# ADR 0002: Risk-based approvals

## Status

Accepted

## Context

Not all tool calls share the same blast radius. Blanket auto-approval is unsafe; blanket human approval is unusable.

## Decision

Use LOW/MEDIUM/HIGH/CRITICAL tiers. CRITICAL blocked by default. HIGH requires human approval. Allowlist remains mandatory for all tiers.

## Consequences

Clear teaching model for governance. Teams can tune thresholds via policy later without rewriting the agent loop.
