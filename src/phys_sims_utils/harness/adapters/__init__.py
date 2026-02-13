"""Simulation adapter contracts and implementations."""

from __future__ import annotations

from typing import Any, Protocol

from phys_sims_utils.shared import EvalResult


class Adapter(Protocol):
    """Protocol for simulator adapters that produce ``EvalResult`` values."""

    def run(self, config: dict[str, Any], seed: int) -> EvalResult:
        """Run one deterministic evaluation for a config/seed pair."""


__all__ = ["Adapter"]
