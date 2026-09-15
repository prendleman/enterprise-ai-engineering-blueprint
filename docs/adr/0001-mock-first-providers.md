# ADR 0001: Mock-first AI providers

## Status

Accepted

## Context

Portfolio demos and CI must run without paid credentials.

## Decision

Default `AI_PROVIDER=mock` with deterministic plans/reviews. Optional OpenAI and Anthropic adapters are explicit opt-in.

## Consequences

Demos are reproducible. Real-provider behavior must be validated separately before production claims.
