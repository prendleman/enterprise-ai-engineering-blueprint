# Project Build Report

## What Was Built

A local-first **reference architecture and working prototype** for governed agentic AI in software engineering. The system accepts a developer task, plans with a provider abstraction (default `mock`), evaluates risk and policy, enforces tool allowlists and human approval gates, executes simulated tools, records telemetry, and surfaces metrics on a Streamlit dashboard — with GitHub governance artifacts and executive documentation.

## Architecture

```text
Developer → Task API → Planner → Policy/Risk → Human Approval → Allowlisted Tools
         → Git/PR Simulator → CI/Security signaling → Reviewer → Telemetry → Dashboard
```

Core packages: `app/agents`, `app/governance`, `app/tools`, `app/telemetry`, `app/security`, `app/api`, `dashboard/`.

## Capabilities Demonstrated

| Capability | Evidence |
| ---------- | -------- |
| Agentic engineering (not a chatbot demo) | Planner / Executor / Reviewer + task orchestration |
| Executable governance | YAML policies, tool registry, approval API, blocked critical path |
| GitHub engineering maturity | CODEOWNERS, PR template, CI/security/release, Dependabot |
| Measurement | SQLite telemetry, metrics API, seeded dashboard |
| Leadership narrative | Executive overview, adoption plan, migration playbook, ADRs |

## Key Files

| Path | Role |
| ---- | ---- |
| `app/services/task_service.py` | End-to-end governed workflow |
| `app/governance/policy_engine.py` | Policy decisions |
| `app/agents/providers.py` | Mock / OpenAI / Anthropic abstraction |
| `config/*.yaml` | Tools, policies, risk, models |
| `scripts/demo.py` | One-command proof |
| `dashboard/app.py` | Executive KPIs |
| `docs/executive-overview.md` | Leadership brief |

## Demo

```bash
python -m pip install -e ".[dev]"
python scripts/seed_metrics.py
python scripts/demo.py
```

Also: `make api`, `make dashboard`, `docker compose up --build`.

**Failure path demonstrated:** unsafe prompt → `BLOCKED` / security policy violation.

## Validation Results

```text
ruff check .     → All checks passed
mypy app         → Success
pytest           → 24 passed
validate_repo.py → PASSED
Engineering Readiness Score → 100 / 100
Coverage → ~90% on app/ (threshold ≥ 80%)
```

## Security and Governance Controls

- Prompt-injection heuristics (`prompt_guard`)
- Secret redaction in logs/telemetry
- Tool allowlist (`shell` / `production_database` disabled)
- Risk levels LOW→CRITICAL; critical non-executable
- Human approval for HIGH via `POST /tasks/{id}/approve`
- Bandit + pip-audit + heuristic secret scan workflow

## Metrics

Delivery, AI system, governance, and **simulated** productivity estimates (`label: simulated_estimate`). Seeded demo data: ~40 synthetic tasks (deterministic seed).

## Simulated Components

- Git branch / PR URLs (`git_simulator`)
- In-flow test/security results for agent tools
- Optional LLM providers (inactive without keys)
- Productivity minutes saved (illustrative model)

## Known Limitations

- GitHub operations are simulated unless integrated with real credentials/apps
- Productivity metrics are simulated estimates
- Prompt-injection defenses are basic heuristics
- This is not a production security boundary
- No production IAM, vault, or SIEM is implemented
- Productivity figures are not experimentally validated ROI

## Resume-Safe Claims

1. Designed and built a reference architecture for governed adoption of agentic AI across enterprise software engineering workflows.
2. Implemented policy-controlled agent tooling, risk-based human approval, automated CI/security validation patterns, simulated Git-based change flow, and engineering telemetry.
3. Developed a metrics framework and dashboard for AI-assisted delivery, governance effectiveness, and clearly labeled simulated developer productivity estimates.
4. Created enterprise adoption, GitHub governance, and repository modernization playbooks with ADRs suitable for engineering and executive audiences.
5. Demonstrated blocked unsafe agent behavior to show that governance controls are enforceable rather than advisory-only.

## Recommended Next Enhancements

- GitHub App + OIDC executor for real PRs
- OPA/Cedar compilation from YAML policies
- OpenTelemetry export to a real observability backend
- Ephemeral sandbox for generated code execution
- Org repository template generator for migration waves
