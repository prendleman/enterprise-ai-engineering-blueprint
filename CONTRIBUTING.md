# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

## Checks before PR

```bash
ruff check .
mypy app
pytest --cov=app
python scripts/validate_repo.py
python scripts/demo.py
```

## Contribution rules

1. Keep claims resume-safe; label simulations explicitly.
2. Do not weaken CRITICAL blocks or approval gates without an ADR.
3. Prefer extending the policy allowlist over adding unconstrained tools.
4. Update docs when governance behavior changes.
