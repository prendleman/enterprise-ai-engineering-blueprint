"""Repository structure validation for the blueprint."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "README.md",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODEOWNERS",
    ".github/workflows/ci.yml",
    ".github/dependabot.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    "app/api.py",
    "app/orchestrator.py",
    "app/tools.py",
    "app/agents.py",
    "app/security.py",
    "app/telemetry.py",
    "dashboard/streamlit_app.py",
    "scripts/demo.py",
    "docs/architecture.md",
    "docs/security-model.md",
    "docs/metrics-framework.md",
    "docs/github-governance.md",
    "docs/enterprise-adoption.md",
    "docs/migration-playbook.md",
    "docs/executive-overview.md",
    "docs/demo-walkthrough.md",
    "docs/adr/0001-mock-first-providers.md",
    "docs/adr/0002-risk-based-approvals.md",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        print("Missing required paths:")
        for path in missing:
            print(f"  - {path}")
        return 1
    print(f"validate_repo OK ({len(REQUIRED)} required paths present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
