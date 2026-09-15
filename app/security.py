"""Security helpers: redaction, injection heuristics, audit events."""

from __future__ import annotations

import logging
import re
from typing import Any

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("generic_token", re.compile(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*['\"]?([^\s'\"]{8,})")),
    ("bearer", re.compile(r"(?i)bearer\s+[a-z0-9\-._~+/]+=*")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")),
]

INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("ignore_policy", re.compile(r"(?i)ignore (all )?(previous|prior|above) (instructions|rules|policies)")),
    ("disable_security", re.compile(r"(?i)disable (all )?(security|safety|guardrails|checks)")),
    ("exfiltrate_env", re.compile(r"(?i)(dump|print|exfiltrate|leak).*(env(ironment)?|secrets?|credentials?)")),
    ("override_approvals", re.compile(r"(?i)(bypass|skip|override).*(approval|policy|human)")),
    ("role_hijack", re.compile(r"(?i)you are now (unrestricted|jailbroken|admin without limits)")),
]

logger = logging.getLogger("eaeb.security")


def redact_secrets(text: str) -> str:
    redacted = text
    for name, pattern in SECRET_PATTERNS:
        if name == "generic_token":
            redacted = pattern.sub(lambda m: f"{m.group(1)}=***REDACTED***", redacted)
        else:
            redacted = pattern.sub("***REDACTED***", redacted)
    return redacted


def detect_prompt_injection(text: str) -> list[str]:
    """Heuristic detector with known false-positive/false-negative limitations.

    This is intentionally shallow. It catches common demo attacks but is not a
    production-grade prompt firewall. Always pair with policy allowlists.
    """
    flags: list[str] = []
    for name, pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            flags.append(name)
    return flags


def audit_event(event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    safe_payload = {k: redact_secrets(str(v)) if isinstance(v, str) else v for k, v in payload.items()}
    event = {"type": event_type, **safe_payload}
    logger.info("audit %s", event)
    return event
