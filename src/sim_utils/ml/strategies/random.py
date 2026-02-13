"""Deterministic random-search strategy."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from sim_utils.ml.param_space import ParameterSpace
from sim_utils.ml.strategies.base import OptimizerStrategy
from sim_utils.shared import Candidate, EvalResult, OptimizationHistory


@dataclass
class RandomStrategy(OptimizerStrategy):
    """Always-available baseline strategy using uniform random sampling."""

    parameter_space: ParameterSpace | None = None
    seed: int = 0
    max_iterations: int | None = None
    _history: list[EvalResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.parameter_space is None:
            from sim_utils.ml.param_space import Parameter

            self.parameter_space = ParameterSpace(
                parameters=(Parameter(name="x", bounds=(0.0, 1.0)),)
            )
        self._rng = random.Random(self.seed)

    def ask(self) -> Candidate:
        parameter_space = self.parameter_space
        if parameter_space is None:  # pragma: no cover - guaranteed by __post_init__
            msg = "parameter_space is required"
            raise RuntimeError(msg)
        theta = {
            parameter.name: self._rng.uniform(parameter.bounds[0], parameter.bounds[1])
            for parameter in parameter_space.parameters
        }
        return Candidate(theta=theta)

    def tell(self, result: EvalResult) -> None:
        self._history.append(result)

    @property
    def is_converged(self) -> bool:
        return self.max_iterations is not None and len(self._history) >= self.max_iterations

    @property
    def result(self) -> OptimizationHistory:
        best = min(self._history, key=lambda item: item.objective) if self._history else None
        return OptimizationHistory(evaluations=tuple(self._history), best=best, seed=self.seed)


__all__ = ["RandomStrategy"]
