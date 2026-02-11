"""Core harness contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from research_utils.shared import EvalResult


@dataclass(frozen=True)
class SweepSpec:
    """Deterministic sweep configuration for multiple evaluations."""

    candidates: tuple[dict[str, float], ...]
    seed: int


@dataclass(frozen=True)
class MetricSpec:
    """Metric declaration consumed by harness reporting."""

    name: str
    goal: str = "min"


@dataclass(frozen=True)
class ReportSpec:
    """Report generation configuration for canonical harness outputs."""

    title: str = "report"
    include_metrics: tuple[str, ...] = ()


class TestHarness(Protocol):
    __test__: bool = False

    """Protocol for adapter-backed harness implementations."""

    name: str

    def run_sweep(self, spec: SweepSpec, metrics: tuple[MetricSpec, ...] = ()) -> list[EvalResult]:
        """Run a deterministic sweep and return canonical eval records."""


@dataclass
class InMemoryTestHarness:
    """Minimal harness implementation for tests and examples."""

    name: str = "default"
    _results: list[EvalResult] = field(default_factory=list)

    def run_sweep(self, spec: SweepSpec, metrics: tuple[MetricSpec, ...] = ()) -> list[EvalResult]:
        _ = metrics
        self._results = [
            EvalResult(
                theta=dict(candidate),
                objective=0.0,
                seed=spec.seed,
                config_hash="",
            )
            for candidate in spec.candidates
        ]
        return list(self._results)
