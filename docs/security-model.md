# Security Model

## Design intent

Agentic workflows introduce a non-human actor into engineering operations. Security controls must therefore bind **identity → authorization → approval → audit** around tool use and change introduction.

## Controls implemented in this prototype

| Control | Implementation |
| ------- | -------------- |
| Prompt suspicion detection | `app/security/prompt_guard.py` |
| Secret redaction in logs/telemetry | `app/security/sanitization.py` |
| Tool allowlist | `config/tools.yaml` + `ToolRegistry` |
| Risk classification | `config/risk_rules.yaml` + `RiskEngine` |
| Human approval gates | `config/policies.yaml` + approval API |
| Critical execution ban | `execution_allowed: false` for critical |
| CI security workflow | Bandit, pip-audit, heuristic secret scan |

## Explicit limitations

This prototype:

- is **not** a production security boundary
- does **not** provide complete prompt-injection protection
- does **not** execute arbitrary generated code
- does **not** include production IAM
- does **not** include production secrets infrastructure
- does **not** integrate with enterprise SIEM/SOAR
- does **not** implement GitHub Enterprise policy APIs

Heuristic prompt checks can be bypassed by novel phrasing. Treat them as a demonstration of *defense-in-depth placement*, not as a guarantee.

## Enterprise deployment target state

| Capability | Production approach |
| ---------- | ------------------- |
| Agent identity | Workload identity (GitHub App / OIDC / SPIFFE) |
| Secrets | Vault / cloud secret manager; short-lived credentials |
| Authorization | Policy engine (OPA/Cedar) with change tickets |
| Code execution | Ephemeral sandboxes with network egress controls |
| Prompt defenses | Layered filters + model-side policies + human review |
| Audit | Immutable event stream to SIEM with retention |
| Runtime | Separate privileged control plane from developer laptops |

## Secure development assumptions for demos

- Default `AI_PROVIDER=mock`
- No API keys required
- Disabled `shell` and `production_database` tools
- Telemetry payloads sanitized before persistence
