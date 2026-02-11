"""Agentic tooling contracts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentArtifact:
    """Generated artifact metadata."""

    path: str


@dataclass
class AgentTool:
    """Base agent tool surface producing artifacts."""

    name: str = "agent-tool"

    def build_artifact(self, path: str) -> AgentArtifact:
        return AgentArtifact(path=path)
