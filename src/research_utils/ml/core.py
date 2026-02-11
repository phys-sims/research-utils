"""Core optimization and parameter-space contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from research_utils.ml.param_space import ParameterSpace
from research_utils.ml.strategies.base import OptimizerStrategy
from research_utils.shared import EvalResult, OptimizationHistory


@dataclass
class OptimizationRunner:
    """Minimal optimization runner with deterministic history."""

    history: list[EvalResult] = field(default_factory=list)

    def record(self, result: EvalResult) -> None:
        self.history.append(result)

    @property
    def result(self) -> OptimizationHistory:
        best = min(self.history, key=lambda item: item.objective) if self.history else None
        return OptimizationHistory(evaluations=tuple(self.history), best=best)


__all__ = ["OptimizationRunner", "OptimizerStrategy", "ParameterSpace"]
