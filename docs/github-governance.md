# GitHub Governance Guide

## Baseline standards

- Protected `main` with required checks
- CODEOWNERS for critical paths
- PR template with risk + validation checklist
- Issue templates for engineering intake
- Dependabot for pip and GitHub Actions
- CI: lint, types, tests, demo, lightweight security scan

## Branching

Prefer short-lived feature branches, squash merges, and no direct commits to `main`.

## AI-assisted contributions

Treat agent-authored diffs like contractor diffs: same review depth, same secret scanning, same ownership rules. Agents do not inherit elevated trust.
