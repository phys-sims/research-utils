"""Optimization runner orchestration with deterministic batching and penalties."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from phys_sims_utils.ml.evaluator import SimulationEvaluator
from phys_sims_utils.ml.logging import OptimizationLogger
from phys_sims_utils.ml.strategies.base import OptimizerStrategy
from phys_sims_utils.shared import EvalResult, OptimizationHistory, Theta


@dataclass
class OptimizationRunner:
    """Run ask/tell optimization loops with deterministic bookkeeping."""

    strategy: OptimizerStrategy | None = None
    evaluator: SimulationEvaluator | Callable[[Theta, int], EvalResult] | None = None
    seed: int = 0
    penalty_objective: float = 1.0e12
    history: list[EvalResult] = field(default_factory=list)
    logger: OptimizationLogger | None = None

    def record(self, result: EvalResult) -> None:
        """Record one evaluation and optionally forward it to a logger."""
        self.history.append(result)
        if self.logger is not None:
            self.logger.log_evaluation(
                iteration=len(self.history) - 1,
                result=result,
                best=self.best,
            )

    @property
    def best(self) -> EvalResult | None:
        """Current best objective in history."""
        return min(self.history, key=lambda item: item.objective) if self.history else None

    @property
    def result(self) -> OptimizationHistory:
        """Optimization history snapshot."""
        return OptimizationHistory(evaluations=tuple(self.history), best=self.best, seed=self.seed)

    def run(self, iterations: int, batch_size: int = 1) -> OptimizationHistory:
        """Run an optimization loop for the requested number of iterations."""
        if iterations < 0:
            msg = "iterations must be >= 0"
            raise ValueError(msg)
        if batch_size <= 0:
            msg = "batch_size must be > 0"
            raise ValueError(msg)
        if self.strategy is None or self.evaluator is None:
            msg = "OptimizationRunner.run requires both strategy and evaluator"
            raise ValueError(msg)

        while len(self.history) < iterations and not self.strategy.is_converged:
            remaining = iterations - len(self.history)
            current_batch = min(batch_size, remaining)
            candidates = [self.strategy.ask() for _ in range(current_batch)]

            for candidate in candidates:
                eval_seed = self.seed + len(self.history)
                result = self._safe_evaluate(theta=candidate.theta, seed=eval_seed)
                self.strategy.tell(result)
                self.record(result)
                if self.strategy.is_converged or len(self.history) >= iterations:
                    break

        if self.logger is not None:
            self.logger.close()
        return self.result

    def _safe_evaluate(self, theta: Theta, seed: int) -> EvalResult:
        evaluator = self.evaluator
        if evaluator is None:
            msg = "OptimizationRunner has no evaluator"
            raise ValueError(msg)

        try:
            if isinstance(evaluator, SimulationEvaluator):
                return evaluator.evaluate(config=theta, seed=seed)
            return evaluator(dict(theta), seed)
        except Exception as exc:  # noqa: BLE001 - convert failures to penalties
            return EvalResult(
                theta=dict(theta),
                objective=self.penalty_objective,
                metrics={"penalty": 1.0},
                artifacts={
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                },
                seed=seed,
            )


__all__ = ["OptimizationRunner"]
