# Contributing

Thank you for contributing to the Enterprise AI Engineering Blueprint.

## Principles

1. Prefer working, testable software over placeholders.
2. Keep mock mode as the default — no paid APIs required for local runs.
3. Clearly label simulated behavior vs. real integrations.
4. Governance, security, and telemetry changes require corresponding tests.
5. Documentation must match implemented behavior.

## Development Setup

```bash
make setup
make test
make lint
make typecheck
make demo
```

Windows (PowerShell):

```powershell
python -m pip install -e ".[dev]"
python scripts/seed_metrics.py
python -m pytest
python -m ruff check .
python -m mypy app
python scripts/demo.py
```

## Pull Requests

Use the PR template. Include:

- Risk level and AI assistance disclosure
- Tests run
- Security impact notes
- Rollback plan when relevant

## Code Style

- Python 3.12+, typed public APIs
- Ruff for lint/format
- mypy strict for `app/`
- Small, readable modules; configuration-driven behavior
