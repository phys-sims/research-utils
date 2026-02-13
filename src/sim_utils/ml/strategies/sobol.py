"""Optional Sobol quasi-random optimization strategy."""

from __future__ import annotations

from dataclasses import dataclass, field

from sim_utils.ml.param_space import ParameterSpace
from sim_utils.ml.strategies.base import OptimizerStrategy
from sim_utils.shared import Candidate, EvalResult, OptimizationHistory

try:  # pragma: no cover - availability is environment dependent
    from scipy.stats import qmc  # type: ignore[import-untyped]
except ImportError:  # pragma: no cover - availability is environment dependent
    qmc = None


@dataclass
class SobolStrategy(OptimizerStrategy):
    """Sobol strategy guarded behind an optional SciPy dependency."""

    parameter_space: ParameterSpace
    seed: int = 0
    max_iterations: int | None = None
    _history: list[EvalResult] = field(default_factory=list)

    def __post_init__(self) -> None:
        if qmc is None:
            msg = "SobolStrategy requires scipy. Install sim-utils[ml] with scipy."
            raise RuntimeError(msg)
        self._engine = qmc.Sobol(
            d=len(self.parameter_space.parameters),
            scramble=True,
            seed=self.seed,
        )

    def ask(self) -> Candidate:
        sample = self._engine.random(1)[0]
        theta = {}
        for index, parameter in enumerate(self.parameter_space.parameters):
            lower, upper = parameter.bounds
            theta[parameter.name] = lower + (upper - lower) * float(sample[index])
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


__all__ = ["SobolStrategy"]
