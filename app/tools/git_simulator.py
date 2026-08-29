"""Simulated Git / pull-request operations (no real GitHub credentials required)."""

from __future__ import annotations

import re
from typing import Any

from app.tools.base import Tool


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:48] or "change"


class GitSimulatorTool(Tool):
    name = "git_simulator"

    def run(self, action: str, context: dict[str, Any]) -> dict[str, Any]:
        task = str(context.get("task", "change"))
        task_id = str(context.get("task_id", "local"))
        branch = f"agent/{_slugify(task)}-{task_id[:8]}"
        pr_number = abs(hash(task_id)) % 9000 + 1000
        return {
            "action": action or "create_branch_and_pr",
            "branch": branch,
            "pr_number": pr_number,
            "pr_url": f"https://github.example.com/org/repo/pull/{pr_number}",
            "title": f"[AI] {task[:72]}",
            "checks": {
                "ci": "queued",
                "security": "queued",
            },
            "simulated": True,
        }
