"""Basic prompt-injection detection for demonstration purposes.

This is intentionally limited. It does not provide complete prompt-injection
protection and should not be treated as a production security boundary.
"""

from __future__ import annotations

from dataclasses import dataclass

SUSPICIOUS_PATTERNS: tuple[str, ...] = (
    "ignore previous instructions",
    "ignore all previous",
    "disable security",
    "reveal secrets",
    "show environment variables",
    "dump environment",
    "bypass approval",
    "execute arbitrary shell",
    "execute arbitrary shell commands",
    "override policy",
    "you are now",
    "jailbreak",
)


@dataclass(frozen=True)
class PromptGuardResult:
    safe: bool
    matched_patterns: list[str]
    reason: str | None = None


def inspect_prompt(prompt: str) -> PromptGuardResult:
    """Flag prompts that attempt to bypass governance controls."""
    lowered = prompt.lower()
    matched = [pattern for pattern in SUSPICIOUS_PATTERNS if pattern in lowered]
    if matched:
        return PromptGuardResult(
            safe=False,
            matched_patterns=matched,
            reason="security policy violation",
        )
    return PromptGuardResult(safe=True, matched_patterns=[])
