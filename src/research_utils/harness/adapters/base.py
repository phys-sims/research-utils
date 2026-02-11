"""Adapter interfaces for simulator integrations."""

from __future__ import annotations

from typing import Any, Protocol

from research_utils.harness import EvalResult


class Adapter(Protocol):
    """Protocol for simulator adapters that produce ``EvalResult`` values."""

    def run(self, config: dict[str, Any], seed: int) -> EvalResult:
        """Run one deterministic evaluation for the given config and seed."""
