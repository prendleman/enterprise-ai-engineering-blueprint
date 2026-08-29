# ADR 0004: Engineering Telemetry

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

AI transformation without measurement becomes narrative. Leadership needs evidence of delivery outcomes, governance effectiveness, and operational risk — not prompt counts alone.

## Decision

Emit structured lifecycle events (`task_started`, `plan_created`, `policy_checked`, `tool_invoked`, `tool_blocked`, etc.) to a local SQLite store. Derive delivery, AI, governance, and clearly labeled simulated productivity metrics for API and dashboard consumption.

## Alternatives Considered

1. **Logs only** — insufficient for aggregation and dashboards.
2. **Immediate dependency on enterprise observability stack** — blocks local demos.
3. **Sampling only final outcomes** — loses diagnostic fidelity for blocked/failed paths.

## Consequences

- Local demo remains self-contained.
- Event schema can later ship to OpenTelemetry / SIEM.
- Productivity estimates must remain labeled as simulated to avoid false ROI claims.
