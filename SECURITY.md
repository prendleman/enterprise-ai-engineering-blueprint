# Security Policy

## Supported versions

This reference blueprint tracks the `main` branch only.

## Reporting a vulnerability

Email the maintainer privately. Do not open a public issue for exploitable findings.

## Security model (summary)

- Tools are allowlisted; unknown tools are blocked.
- CRITICAL risk actions are blocked by default.
- HIGH risk actions require human approval.
- Prompt-injection detection is heuristic and **not** a complete control.
- Secrets are redacted in audit logs when matched by known patterns.
- Default runtime uses the **mock** provider and needs no API keys.

## Limitations

This repository is a portfolio/reference implementation. Controls are intentionally transparent for teaching and demonstration. They are not a substitute for a production security program, SIEM, or LLM firewall.
