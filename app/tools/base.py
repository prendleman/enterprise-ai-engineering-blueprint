"""Tool base types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Base class for agent-invoked tools."""

    name: str

    @abstractmethod
    def run(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool action and return a structured result."""
