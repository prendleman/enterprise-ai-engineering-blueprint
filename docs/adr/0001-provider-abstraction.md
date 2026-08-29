# ADR 0001: Provider Abstraction

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Enterprises evaluating agentic engineering cannot afford hard-coding a single model vendor. Procurement, data residency, cost, and quality characteristics change. Local demos must also run without paid credentials.

## Decision

Introduce an `AIProvider` interface with `generate_plan(task) -> AgentPlan` and concrete implementations for `mock`, `openai`, and `anthropic`. Provider selection is environment-driven (`AI_PROVIDER`), with automatic fallback to `mock` when credentials are absent.

## Alternatives Considered

1. **Single-vendor SDK embedded in agents** — simpler short-term, creates lock-in.
2. **HTTP-only gateway to a corporate LLM proxy** — ideal later, but blocks offline demos.
3. **Prompt files without a typed interface** — weak testability and inconsistent outputs.

## Consequences

- Agents depend on a stable contract, not a vendor SDK.
- Mock mode enables CI and recruiter demos without secrets.
- Real providers remain optional extras with clear env requirements.
- Plan quality may differ by provider; governance still applies uniformly after planning.
