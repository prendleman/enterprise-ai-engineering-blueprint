# Security Model

## Risk tiers

| Risk | Default behavior |
|------|------------------|
| LOW | Auto-execute if allowlisted |
| MEDIUM | Auto-execute if allowlisted; audited |
| HIGH | Human approval required |
| CRITICAL | Blocked by default |

## Controls

1. **Allowlist** — only registered tools may run
2. **Risk gate** — CRITICAL never executes in default policy
3. **Approval gate** — HIGH waits for human decision
4. **Injection heuristics** — common jailbreak / exfil phrases flagged
5. **Redaction** — tokens/keys scrubbed from audit strings
6. **Audit trail** — structured events per task lifecycle

## Explicit limitations

- Heuristic injection detection has false positives/negatives.
- Mock Git/CI tools do not touch real repositories unless you replace handlers.
- Optional OpenAI/Anthropic adapters transmit prompts to third parties when enabled.
