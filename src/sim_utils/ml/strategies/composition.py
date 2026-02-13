"""Composable optimization strategies built on top of ask/tell contracts."""

from __future__ import annotations

from dataclasses import dataclass, field

from sim_utils.ml.strategies.base import OptimizerStrategy
from sim_utils.shared import Candidate, EvalResult, OptimizationHistory


@dataclass
class StagedStrategy(OptimizerStrategy):
    """Run strategies in sequence with deterministic stage transition rules."""

    stages: tuple[OptimizerStrategy, ...]
    stage_max_iterations: tuple[int, ...] | None = None
    _history: list[EvalResult] = field(default_factory=list)
    _current_stage_index: int = 0

    def __post_init__(self) -> None:
        if not self.stages:
            msg = "StagedStrategy requires at least one stage"
            raise ValueError(msg)
        if self.stage_max_iterations is not None and len(self.stage_max_iterations) != len(
            self.stages
        ):
            msg = "stage_max_iterations must match number of stages"
            raise ValueError(msg)

    def ask(self) -> Candidate:
        self._advance_if_needed()
        return self.stages[self._current_stage_index].ask()

    def tell(self, result: EvalResult) -> None:
        self.stages[self._current_stage_index].tell(result)
        self._history.append(result)
        self._advance_if_needed()

    @property
    def is_converged(self) -> bool:
        return self._current_stage_index >= len(self.stages) - 1 and self.stages[
            self._current_stage_index
        ].is_converged

    @property
    def result(self) -> OptimizationHistory:
        best = min(self._history, key=lambda item: item.objective) if self._history else None
        return OptimizationHistory(evaluations=tuple(self._history), best=best)

    def _advance_if_needed(self) -> None:
        while self._current_stage_index < len(self.stages) - 1:
            stage = self.stages[self._current_stage_index]
            if self._stage_complete(stage_index=self._current_stage_index, stage=stage):
                self._current_stage_index += 1
                continue
            break

    def _stage_complete(self, stage_index: int, stage: OptimizerStrategy) -> bool:
        if stage.is_converged:
            return True
        if self.stage_max_iterations is None:
            return False
        max_iterations = self.stage_max_iterations[stage_index]
        if max_iterations < 0:
            msg = "stage_max_iterations values must be >= 0"
            raise ValueError(msg)
        return len(stage.result.evaluations) >= max_iterations


@dataclass
class PortfolioStrategy(OptimizerStrategy):
    """Dispatch ask/tell calls across strategies with deterministic round-robin allocation."""

    strategies: tuple[OptimizerStrategy, ...]
    _history: list[EvalResult] = field(default_factory=list)
    _next_strategy_index: int = 0
    _pending_owner_indices: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.strategies:
            msg = "PortfolioStrategy requires at least one strategy"
            raise ValueError(msg)

    def ask(self) -> Candidate:
        for _ in range(len(self.strategies)):
            strategy = self.strategies[self._next_strategy_index]
            owner_index = self._next_strategy_index
            self._next_strategy_index = (self._next_strategy_index + 1) % len(
                self.strategies
            )
            if strategy.is_converged:
                continue
            self._pending_owner_indices.append(owner_index)
            return strategy.ask()

        msg = "all portfolio strategies are converged"
        raise RuntimeError(msg)

    def tell(self, result: EvalResult) -> None:
        if not self._pending_owner_indices:
            msg = "PortfolioStrategy.tell called before ask"
            raise RuntimeError(msg)
        owner_index = self._pending_owner_indices.pop(0)
        self.strategies[owner_index].tell(result)
        self._history.append(result)

    @property
    def is_converged(self) -> bool:
        return all(strategy.is_converged for strategy in self.strategies)

    @property
    def result(self) -> OptimizationHistory:
        best = min(self._history, key=lambda item: item.objective) if self._history else None
        return OptimizationHistory(evaluations=tuple(self._history), best=best)


__all__ = ["PortfolioStrategy", "StagedStrategy"]
