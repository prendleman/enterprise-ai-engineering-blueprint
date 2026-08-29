# ADR 0005: Mock-First Local Development

- **Status:** Accepted
- **Date:** 2026-08-29

## Context

Reference repositories that require paid APIs fail as resume artifacts, CI defaults, and classroom/lab environments. Credential friction also encourages committing secrets.

## Decision

Default `AI_PROVIDER=mock` with deterministic plan generation and simulated Git/PR/test tools. Optional OpenAI/Anthropic providers activate only when environment variables and packages are present.

## Alternatives Considered

1. **Require OpenAI for all demos** — excludes many evaluators; increases secret risk.
2. **Recorded HTTP cassettes only** — brittle across provider API changes.
3. **Fully offline LLM weights** — heavyweight for a blueprint repository.

## Consequences

- `make demo` works on a clean machine.
- CI remains deterministic and free.
- Users must understand mock outputs are illustrative, not model-quality benchmarks.
- Real provider paths remain available for teams with approved keys.
