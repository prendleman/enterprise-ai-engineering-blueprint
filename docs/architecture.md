# Architecture

Agentic development changes the engineering control surface: an additional actor can select tools, generate changes, and initiate operations. Authorization, approval, auditability, and measurement must therefore be first-class.

## Runtime flow

1. Task intake (API / dashboard / demo script)
2. Prompt-injection heuristics + secret redaction
3. Planner agent produces a risk-annotated plan
4. Policy engine evaluates tool allowlist + risk tier
5. Executor runs allowed tools (simulated Git/CI by default)
6. Human approval gate for HIGH risk
7. Reviewer agent validates outcomes
8. Telemetry written to DuckDB for engineering metrics

## Components

- `app/providers.py` — mock-first AI providers
- `app/tools.py` — least-privilege tool registry
- `app/agents.py` — planner / executor / reviewer roles
- `app/orchestrator.py` — governed workflow state machine
- `app/api.py` — FastAPI control plane
- `dashboard/streamlit_app.py` — operator dashboard
