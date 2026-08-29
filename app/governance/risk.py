"""Risk classification for agent tasks."""

from __future__ import annotations

from app.models import RiskLevel
from app.settings import load_yaml


class RiskEngine:
    """Score task text against configurable keyword risk rules."""

    def __init__(self) -> None:
        self._config = load_yaml("risk_rules.yaml")

    def assess(self, task: str, tools_requested: list[str] | None = None) -> RiskLevel:
        """Return the highest risk level implied by the task and tools."""
        lowered = task.lower()
        levels: list[RiskLevel] = []

        for rule in self._config.get("keyword_rules", []):
            risk = RiskLevel(str(rule["risk"]).lower())
            patterns = [str(p).lower() for p in rule.get("patterns", [])]
            if any(pattern in lowered for pattern in patterns):
                levels.append(risk)

        tools_requested = tools_requested or []
        tool_risks = self._tool_risks()
        for tool in tools_requested:
            if tool in tool_risks:
                levels.append(tool_risks[tool])

        if not levels:
            default = str(self._config.get("default_risk", "medium")).lower()
            return RiskLevel(default)
        return max(levels, key=self.score)

    def _tool_risks(self) -> dict[str, RiskLevel]:
        tools_cfg = load_yaml("tools.yaml").get("tools", {})
        result: dict[str, RiskLevel] = {}
        for name, meta in tools_cfg.items():
            result[name] = RiskLevel(str(meta.get("risk", "medium")).lower())
        return result

    @staticmethod
    def score(level: RiskLevel) -> int:
        order = {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }
        return order[level]
