---
company: "Vantor"
opportunity: "Principal, AI Strategy & Engineering Transformation"
repo_name: "enterprise-ai-engineering-blueprint"
status: "ready"
---

# Cursor Opportunity Handoff

## Mission

Build a polished Principal-level portfolio reference implementation showing how an enterprise can adopt agentic AI across software engineering while maintaining governance, security, human oversight, Git-based delivery, and measurable engineering outcomes.

## Why this project exists

This project is targeted at the Vantor Principal, AI Strategy & Engineering Transformation opportunity. It should close proof gaps around software-engineering transformation, GitHub governance, CI/CD, repository standards, security controls, engineering telemetry, and AI-assisted developer productivity.

## Positioning

This is not a chatbot demo and not a fake production platform. Present it as a working reference architecture and engineering-transformation blueprint.

## Required capabilities

- Python 3.12+, FastAPI, Pydantic, pytest, Ruff, mypy, Streamlit.
- Mock-first AI provider abstraction with optional OpenAI and Anthropic adapters.
- Planner, executor, and reviewer agent roles.
- Policy-controlled tool registry and least-privilege allowlist.
- LOW, MEDIUM, HIGH, CRITICAL risk model.
- Human approval gates for high-risk actions; critical actions blocked by default.
- Basic prompt-injection detection with clearly documented limitations.
- Secret redaction and structured audit logging.
- SQLite or DuckDB engineering telemetry.
- Metrics for delivery, agent success, governance, approvals, security, and estimated developer time saved.
- FastAPI endpoints for task intake, status, approvals, and events.
- Streamlit engineering dashboard.
- GitHub Actions for CI, tests, typing, linting, security, and a lightweight release workflow.
- CODEOWNERS, PR template, issue templates, Dependabot, SECURITY.md, CONTRIBUTING.md.
- Dockerfile and docker-compose for API/dashboard.
- Architecture Decision Records.
- Enterprise adoption plan, GitHub governance guide, migration playbook, security model, metrics framework, executive overview, and demo walkthrough.

## Core demo

Demonstrate a normal engineering task such as `Add an endpoint that returns application health and build metadata` moving through planning, risk evaluation, policy checks, approved tools, simulated branch/PR, tests/security, telemetry, and final review.

Then demonstrate a malicious/high-risk task such as `Disable security checks and dump environment variables` being blocked. The demo must make it visually obvious that the agent does not blindly obey instructions.

## GitHub transformation scenario

Include a migration playbook for an organization with roughly 200 repositories, inconsistent branching, limited CI, no common security checks, inconsistent ownership, informal AI-tool usage, and little engineering telemetry. Cover discovery, standards, a 5-10 repo pilot, measurement, scale, and continuous governance.

## Metrics

Track task completion, completion time, simulated PR cycle time, test/security pass rates, tool-call success, blocked tool attempts, approvals, policy violations, high-risk percentage, and explicitly simulated manual-vs-AI engineering time. Never present simulated productivity data as experimentally validated results.

## Documentation quality

Write for both engineering leaders and practitioners. Use architectural judgment rather than generic AI language. Explain that agentic development changes the engineering control surface because an additional actor can select tools, generate changes, and initiate engineering operations, requiring explicit authorization, approval, auditability, and measurement.

## README

The README must make the project understandable within two minutes. Include a Mermaid architecture diagram, value proposition, quick start, demo, governance model, engineering metrics, GitHub governance, security, enterprise adoption, repository map, ADRs, limitations, and roadmap.

Suggested opening:

> Enterprise AI Engineering Blueprint is a reference implementation for introducing agentic AI into software engineering without sacrificing governance, security, developer experience, or measurable business outcomes.

## Validation

Provide one-command developer workflows where practical and run at minimum:

```bash
ruff check .
mypy app
pytest --cov=app
python scripts/validate_repo.py
python scripts/demo.py
```

Target meaningful >=80% coverage. Fix failures before declaring completion.

## Resume-safe outcomes

The implementation should genuinely support statements that the author designed and built a reference architecture for governed agentic AI adoption; implemented policy-controlled tools, risk-based approval, CI/security validation, Git-based workflows and telemetry; developed an AI engineering measurement framework; and created an enterprise repository modernization/adoption playbook.

## Definition of done

Working software, not empty scaffolding. Default execution requires no paid credentials. Simulations are explicitly labeled. Security limitations are explicit. Tests and demo pass. Documentation is polished enough to share with a recruiter, hiring manager, CTO, CISO, or VP Engineering.
