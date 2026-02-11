"""Built-in optimization strategies."""

from dataclasses import dataclass, field

from research_utils.ml.strategies.base import OptimizerStrategy
from research_utils.shared import Candidate, EvalResult, OptimizationHistory


@dataclass
class RandomSearchStrategy:
    """Placeholder deterministic strategy for import-surface stability."""

    seed: int = 0
    _history: list[EvalResult] = field(default_factory=list)

    def ask(self) -> Candidate:
        return Candidate(theta={"x": float(self.seed + len(self._history))})

    def tell(self, result: EvalResult) -> None:
        self._history.append(result)

    @property
    def is_converged(self) -> bool:
        return False

    @property
    def result(self) -> OptimizationHistory:
        best = min(self._history, key=lambda item: item.objective) if self._history else None
        return OptimizationHistory(evaluations=tuple(self._history), best=best, seed=self.seed)


__all__ = ["OptimizerStrategy", "RandomSearchStrategy"]
