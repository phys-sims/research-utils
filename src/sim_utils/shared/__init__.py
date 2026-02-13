"""Shared utility exports."""

from dataclasses import dataclass

from sim_utils.shared.types import (
    Candidate,
    EvalResult,
    OptimizationHistory,
    SweepResult,
    Theta,
)


@dataclass(frozen=True)
class Seed:
    """Simple explicit seed wrapper."""

    value: int


__all__ = [
    "Candidate",
    "EvalResult",
    "OptimizationHistory",
    "Seed",
    "SweepResult",
    "Theta",
]
