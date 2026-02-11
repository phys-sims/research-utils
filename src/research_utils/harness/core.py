"""Core harness contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvalResult:
    """Canonical evaluation result shared across harness and ML."""

    objective: float
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestHarness:
    __test__ = False

    """Minimal harness surface for adapter-backed evaluations."""

    name: str = "default"

    def evaluate(self, objective: float, metrics: dict[str, float] | None = None) -> EvalResult:
        """Build an ``EvalResult`` from deterministic caller-provided values."""
        return EvalResult(objective=objective, metrics=metrics or {})
