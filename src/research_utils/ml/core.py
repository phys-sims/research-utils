"""Core optimization and parameter-space contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class ParameterSpace:
    """Minimal stable parameter-space contract."""

    names: tuple[str, ...] = ()

    def encode(self, values: dict[str, float]) -> tuple[float, ...]:
        return tuple(values[name] for name in self.names)


class OptimizerStrategy(Protocol):
    """Shared ask/tell strategy interface."""

    def ask(self) -> dict[str, float]:
        """Request the next candidate point."""

    def tell(self, result: float) -> None:
        """Report objective feedback."""


@dataclass
class OptimizationRunner:
    """Minimal optimization runner with deterministic history."""

    history: list[float] = field(default_factory=list)

    def record(self, objective: float) -> None:
        self.history.append(objective)
