"""Tool package exports and factory."""

from __future__ import annotations

from app.tools.base import Tool
from app.tools.code_analyzer import CodeAnalyzerTool
from app.tools.file_reader import FileReaderTool
from app.tools.git_simulator import GitSimulatorTool
from app.tools.test_runner import TestRunnerTool


def build_tool_catalog() -> dict[str, Tool]:
    tools: list[Tool] = [
        FileReaderTool(),
        CodeAnalyzerTool(),
        TestRunnerTool(),
        GitSimulatorTool(),
    ]
    return {tool.name: tool for tool in tools}


__all__ = [
    "CodeAnalyzerTool",
    "FileReaderTool",
    "GitSimulatorTool",
    "TestRunnerTool",
    "Tool",
    "build_tool_catalog",
]
