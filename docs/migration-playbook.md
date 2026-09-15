# Migration Playbook (~200 repositories)

## Starting conditions (typical)

- Inconsistent branching
- Limited CI
- No common security checks
- Inconsistent ownership
- Informal AI-tool usage
- Little engineering telemetry

## Wave plan

### Wave 0 — Discovery (2–3 weeks)
Inventory languages, default branches, CI presence, CODEOWNERS, secrets scanning, and open critical vulns.

### Wave 1 — Foundations
Org-level templates, required workflow starter, Dependabot, SECURITY.md, and branch protection reference policy.

### Wave 2 — Pilot (5–10 repos)
Select representative services. Enable governed agent blueprint, collect metrics, tune approval friction.

### Wave 3 — Scale by platform cohort
Migrate in batches of 20–30 repos. Block merge without required checks. Track adoption dashboards.

### Wave 4 — Continuous governance
Exception process, model/provider review, quarterly drift detection for repos that disable controls.

## Success criteria

- ≥90% repos with required CI
- CODEOWNERS coverage on critical paths
- Measurable decline in policy-violating AI actions
- Clear simulated-vs-real labeling in leadership reporting
