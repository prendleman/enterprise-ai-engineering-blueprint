# Migration Playbook

## Scenario

An engineering organization operates approximately **200 repositories** with:

- Inconsistent branching strategies
- Limited or uneven CI
- No common security checks
- Inconsistent ownership
- Informal AI tool usage
- Little engineering telemetry

Goal: migrate from unmanaged repositories into governed engineering workflows that can safely host agentic AI assistance.

---

## Phase 1: Discovery

Inventory each repository for:

- Language and package manager
- Build and test commands
- Owners / CODEOWNERS gaps
- CI presence and reliability
- Secret exposure indicators
- Dependency risk
- Current AI tooling usage (survey)

**Output:** prioritized heat map (critical systems vs. low-risk services).

## Phase 2: Standards

Define an organization baseline:

- Trunk-based or short-lived branch strategy
- PR template including AI assistance disclosure
- CODEOWNERS required for sensitive paths
- Mandatory CI jobs (lint, types, tests)
- Mandatory security jobs (dependency + SAST heuristics)
- AI usage policy and tool allowlist
- Telemetry event schema

**Output:** approved engineering standard + reference template repository.

## Phase 3: Pilot

Select 5–10 representative repositories spanning:

- Service API
- Internal library
- Data job
- Frontend app
- Infrastructure-adjacent repo (higher governance)

Deploy governance, CI/security, AI workflow integration, and telemetry. Keep production credentials out of agent tool access.

## Phase 4: Measure

Compare pilot vs. baseline on:

- PR cycle time
- Deployment frequency
- Change failure rate
- Test pass rate
- Security findings opened/closed
- Developer satisfaction
- AI-assisted task completion (with clear estimate labeling)

Avoid rewarding raw commit volume.

## Phase 5: Scale

Create reusable assets:

- Repository template with workflows and docs
- Policy packs (`tools.yaml` / `policies.yaml` equivalents)
- Automated readiness scorecard
- Wave-based migration with platform support hours

## Phase 6: Continuous Governance

Stand up:

- Engineering / AI governance board
- Scorecards reviewed monthly
- Exception process with expiry dates
- Red-team exercises for prompt injection and tool misuse
- Periodic policy recalibration

## Anti-patterns to avoid

- Enabling agents before branch protection
- Granting shell/production tools “temporarily”
- Measuring success only by number of AI prompts
- Rolling out to regulated systems first
