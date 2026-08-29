#!/usr/bin/env python3
"""Validate repository structure and compute engineering readiness scorecard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_PATHS = [
    "README.md",
    "BUILD_SPEC.md",
    "BUILD_REPORT.md",
    "LICENSE",
    "pyproject.toml",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    ".env.example",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODEOWNERS",
    "app/main.py",
    "app/api/routes.py",
    "app/agents/planner.py",
    "app/agents/executor.py",
    "app/agents/reviewer.py",
    "app/agents/providers.py",
    "app/governance/policy_engine.py",
    "app/governance/risk.py",
    "app/governance/approvals.py",
    "app/governance/tool_registry.py",
    "app/telemetry/events.py",
    "app/telemetry/metrics.py",
    "app/security/prompt_guard.py",
    "dashboard/app.py",
    "config/policies.yaml",
    "config/tools.yaml",
    "config/risk_rules.yaml",
    "config/models.yaml",
    "scripts/demo.py",
    "scripts/seed_metrics.py",
    "tests/test_api.py",
    "docs/architecture.md",
    "docs/executive-overview.md",
    "docs/enterprise-adoption.md",
    "docs/github-governance.md",
    "docs/migration-playbook.md",
    "docs/security-model.md",
    "docs/metrics-framework.md",
    "docs/demo-walkthrough.md",
    "docs/adr/0001-provider-abstraction.md",
    "docs/adr/0002-human-approval-gates.md",
    "docs/adr/0003-policy-driven-tool-access.md",
    "docs/adr/0004-engineering-telemetry.md",
    "docs/adr/0005-mock-first-local-development.md",
    ".github/workflows/ci.yml",
    ".github/workflows/security.yml",
    ".github/workflows/release.yml",
    ".github/dependabot.yml",
    ".github/pull_request_template.md",
]

SCORECARD_CHECKS = [
    ("CI enabled", ".github/workflows/ci.yml", 12),
    ("Security workflow enabled", ".github/workflows/security.yml", 12),
    ("CODEOWNERS present", "CODEOWNERS", 10),
    ("PR template present", ".github/pull_request_template.md", 8),
    ("Tests present", "tests/test_governance.py", 12),
    ("Documentation present", "docs/executive-overview.md", 10),
    ("AI policy configured", "config/policies.yaml", 12),
    ("Telemetry configured", "app/telemetry/repository.py", 12),
    ("Docker packaging", "Dockerfile", 6),
    ("Demo script", "scripts/demo.py", 6),
]


def validate() -> list[str]:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).exists()]
    return missing


def scorecard() -> tuple[int, list[tuple[str, bool, int]]]:
    results: list[tuple[str, bool, int]] = []
    score = 0
    for label, path, points in SCORECARD_CHECKS:
        ok = (ROOT / path).exists()
        results.append((label, ok, points))
        if ok:
            score += points
    return score, results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scorecard", action="store_true", help="Print readiness scorecard")
    parser.parse_args()

    missing = validate()
    if missing:
        print("Repository validation FAILED. Missing:")
        for path in missing:
            print(f"  - {path}")
        sys.exit(1)

    print("Repository validation PASSED.")
    print(f"Checked {len(REQUIRED_PATHS)} required paths.")

    total = sum(points for _, _, points in SCORECARD_CHECKS)
    score, results = scorecard()
    print()
    print(f"Engineering Readiness Score: {score} / {total}")
    print("Calculation: sum of weighted control checks present in the repository.")
    for label, ok, points in results:
        mark = "PASS" if ok else "MISS"
        print(f"  [{mark}] {label} (+{points})")


if __name__ == "__main__":
    main()
