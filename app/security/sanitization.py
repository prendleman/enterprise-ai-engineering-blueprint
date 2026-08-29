"""Text sanitization and secret redaction."""

from __future__ import annotations

from typing import Any

from app.security.secrets import SECRET_PATTERNS

REDACTED = "[REDACTED]"
SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "authorization",
    "access_token",
    "refresh_token",
}


def sanitize_text(text: str) -> str:
    """Redact common secret patterns from free-form text."""
    sanitized = text
    for pattern in SECRET_PATTERNS:
        sanitized = pattern.sub(REDACTED, sanitized)
    return sanitized


def sanitize_payload(payload: Any) -> Any:
    """Recursively sanitize strings inside nested structures."""
    if isinstance(payload, str):
        return sanitize_text(payload)
    if isinstance(payload, dict):
        clean: dict[str, Any] = {}
        for key, value in payload.items():
            key_str = str(key)
            if key_str.lower().replace("-", "_") in SENSITIVE_KEYS:
                clean[key_str] = REDACTED
            else:
                clean[key_str] = sanitize_payload(value)
        return clean
    if isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    return payload
