"""Optional CMA-ES optimization strategy."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

from phys_sims_utils.ml.param_space import ParameterSpace
from phys_sims_utils.ml.strategies.base import OptimizerStrategy
from phys_sims_utils.shared import Candidate, EvalResult, OptimizationHistory

try:  # pragma: no cover - availability is environment dependent
    _cma: Any = import_module("cma")
except ImportError:  # pragma: no cover - availability is environment dependent
    _cma = None


@dataclass
class CMAESStrategy(OptimizerStrategy):
    """CMA-ES strategy guarded behind the optional ``cma`` dependency."""

    parameter_space: ParameterSpace
    seed: int = 0
    sigma0: float | None = None
    max_iterations: int | None = None
    _history: list[EvalResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        if _cma is None:
            msg = (
                "CMAESStrategy requires the optional 'cma' package. "
                "Install it with 'pip install phys-sims-utils[ml] cma'."
            )
            raise RuntimeError(msg)

        lowers: list[float] = []
        uppers: list[float] = []
        for parameter in self.parameter_space.parameters:
            if parameter.bounds is None:
                msg = (
                    "CMAESStrategy requires bounded numeric parameters; "
                    f"'{parameter.name}' is categorical"
                )
                raise ValueError(msg)
            lowers.append(float(parameter.bounds[0]))
            uppers.append(float(parameter.bounds[1]))
        for lower, upper, parameter in zip(
            lowers, uppers, self.parameter_space.parameters, strict=True
        ):
            if lower == upper:
                msg = (
                    f"CMAESStrategy requires non-degenerate bounds; "
                    f"'{parameter.name}' has bounds ({lower}, {upper})."
                )
                raise ValueError(msg)

        x0 = [(lower + upper) / 2.0 for lower, upper in zip(lowers, uppers, strict=True)]
        if self.sigma0 is None:
            avg_span = sum((upper - lower) for lower, upper in zip(lowers, uppers, strict=True))
            self.sigma0 = avg_span / max(len(lowers), 1) / 3.0

        options = {
            "bounds": [lowers, uppers],
            "seed": self.seed,
            "verbose": -9,
            "verb_log": 0,
        }
        self._optimizer = _cma.CMAEvolutionStrategy(x0, self.sigma0, options)

    def ask(self) -> Candidate:
        encoded = self._optimizer.ask(1)[0]
        theta: dict[str, float] = {}
        for index, parameter in enumerate(self.parameter_space.parameters):
            if parameter.bounds is None:
                msg = (
                    "CMAESStrategy requires bounded numeric parameters; "
                    f"'{parameter.name}' is categorical"
                )
                raise ValueError(msg)
            lower, upper = parameter.bounds
            value = float(encoded[index])
            clipped = min(max(value, lower), upper)
            theta[parameter.name] = clipped
        return Candidate(theta=theta)

    def tell(self, result: EvalResult) -> None:
        encoded = [
            float(result.theta[parameter.name])
            for parameter in self.parameter_space.parameters
        ]
        self._optimizer.tell([encoded], [float(result.objective)])
        self._history.append(result)

    @property
    def is_converged(self) -> bool:
        by_iterations = (
            self.max_iterations is not None and len(self._history) >= self.max_iterations
        )
        return bool(by_iterations or self._optimizer.stop())

    @property
    def result(self) -> OptimizationHistory:
        best = min(self._history, key=lambda item: item.objective) if self._history else None
        return OptimizationHistory(evaluations=tuple(self._history), best=best, seed=self.seed)


__all__ = ["CMAESStrategy"]
