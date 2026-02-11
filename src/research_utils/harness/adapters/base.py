"""Adapter interfaces for simulator integrations."""

from __future__ import annotations

from typing import Protocol

from research_utils.harness import EvalResult


class Adapter(Protocol):
    """Protocol for simulator adapters that produce ``EvalResult`` values."""

    def run(self) -> EvalResult:
        """Run one deterministic evaluation."""
