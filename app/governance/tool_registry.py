"""Tool allowlist registry backed by YAML configuration."""

from __future__ import annotations

from dataclasses import dataclass

from app.models import RiskLevel
from app.settings import load_yaml


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    enabled: bool
    risk: RiskLevel
    description: str


class ToolRegistry:
    """Least-privilege tool catalog for agent execution."""

    def __init__(self) -> None:
        raw = load_yaml("tools.yaml").get("tools", {})
        self._tools: dict[str, ToolDefinition] = {}
        for name, meta in raw.items():
            self._tools[name] = ToolDefinition(
                name=name,
                enabled=bool(meta.get("enabled", False)),
                risk=RiskLevel(str(meta.get("risk", "medium")).lower()),
                description=str(meta.get("description", "")),
            )

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def is_enabled(self, name: str) -> bool:
        tool = self._tools.get(name)
        return bool(tool and tool.enabled)

    def enabled_tools(self) -> list[str]:
        return [name for name, tool in self._tools.items() if tool.enabled]

    def filter_allowed(self, requested: list[str]) -> tuple[list[str], list[str]]:
        """Split requested tools into allowed and blocked."""
        allowed: list[str] = []
        blocked: list[str] = []
        for name in requested:
            if self.is_enabled(name):
                allowed.append(name)
            else:
                blocked.append(name)
        return allowed, blocked

    def all_tools(self) -> dict[str, ToolDefinition]:
        return dict(self._tools)
