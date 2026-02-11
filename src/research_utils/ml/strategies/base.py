"""Base strategy contracts for optimizer ask/tell flows."""

from __future__ import annotations

from typing import Protocol

from research_utils.shared import Candidate, EvalResult, OptimizationHistory


class OptimizerStrategy(Protocol):
    """Optimizer strategy contract with deterministic ask/tell semantics."""

    def ask(self) -> Candidate:
        """Return the next candidate to evaluate."""

    def tell(self, result: EvalResult) -> None:
        """Record evaluation feedback for a previously asked candidate."""

    @property
    def is_converged(self) -> bool:
        """Whether the strategy considers the optimization converged."""

    @property
    def result(self) -> OptimizationHistory:
        """Current optimization history and best-known result."""
