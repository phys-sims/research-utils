"""Simulation evaluator abstractions for optimization workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sim_utils.harness.adapters import Adapter
from sim_utils.shared import EvalResult


@dataclass(frozen=True)
class SimulationEvaluator:
    """Deterministic wrapper around an adapter that returns objective + metrics."""

    adapter: Adapter

    def evaluate(self, config: dict[str, Any], seed: int) -> EvalResult:
        """Run one deterministic simulation evaluation."""
        return self.adapter.run(config=config, seed=seed)

    def objective_and_metrics(
        self,
        config: dict[str, Any],
        seed: int,
    ) -> tuple[float, dict[str, float]]:
        """Return objective scalar and a copy of metrics dictionary."""
        result = self.evaluate(config=config, seed=seed)
        return result.objective, dict(result.metrics)


__all__ = ["SimulationEvaluator"]
