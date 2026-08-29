# GitHub Governance

Agentic AI does not replace GitHub as the system of record for engineering change. It increases the importance of branch protection, ownership, and required evidence.

## Demonstrated in this repository

| Control | Artifact |
| ------- | -------- |
| CODEOWNERS | `/CODEOWNERS` (placeholder teams) |
| PR template with AI disclosure | `.github/pull_request_template.md` |
| CI validation | `.github/workflows/ci.yml` |
| Security scanning workflow | `.github/workflows/security.yml` |
| Release simulation | `.github/workflows/release.yml` |
| Dependency updates | `.github/dependabot.yml` |
| Issue templates | `.github/ISSUE_TEMPLATE/` |

Replace `@platform-engineering` and `@security-engineering` with real GitHub team handles in your organization.

## Requires configuration in GitHub (not fully enforceable by files alone)

These controls must be configured as **repository rulesets** or classic branch protection:

- Require pull requests before merging
- Require at least one approving review
- Require review from CODEOWNERS
- Require status checks (CI + security)
- Require conversation resolution
- Prevent force pushes
- Prevent branch deletion
- Restrict who can bypass protections
- Optional: require signed commits / deploy environments

**Important distinction:** Workflow YAML proves checks *exist*. Rulesets determine whether merges are *blocked* when checks fail.

## Recommended ruleset posture for agent-generated changes

1. Treat agent-opened PRs like human PRs — no bypass path for bots on protected branches.
2. Require security workflow success on default branch updates.
3. Route `/app/security` and `/config` changes to security CODEOWNERS.
4. Disallow direct pushes to `main` for all identities, including automation.
5. Log automation identities distinctly for audit (GitHub App recommended in production).

## Integration points (not implemented here)

- GitHub Apps / installation tokens for PR creation
- OIDC federation to cloud providers
- Enterprise secret scanning / push protection
- Advanced Security features where licensed

This blueprint intentionally stops at portable, free-tooling patterns so the demo runs without enterprise licenses.
