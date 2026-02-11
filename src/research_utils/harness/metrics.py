"""Metric computation and aggregation for harness evaluations."""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Callable, Protocol, Sequence


class SupportsEvalResult(Protocol):
    @property
    def objective(self) -> float: ...

    @property
    def metrics(self) -> dict[str, float]: ...


MetricFn = Callable[[SupportsEvalResult], float]


@dataclass(frozen=True)
class MetricSpec:
    """Configurable metric computation and aggregation contract."""

    metric_fns: dict[str, MetricFn] = field(default_factory=dict)
    aggregations: tuple[str, ...] = ("mean", "min", "max")
    include_objective: bool = True

    def compute(self, result: SupportsEvalResult) -> dict[str, float]:
        metrics = dict(result.metrics)
        if self.include_objective:
            metrics.setdefault("objective", result.objective)
        for name, func in self.metric_fns.items():
            metrics[name] = float(func(result))
        return metrics

    def aggregate(self, results: Sequence[SupportsEvalResult]) -> dict[str, float]:
        if not results:
            return {}

        per_metric: dict[str, list[float]] = {}
        for result in results:
            for name, value in self.compute(result).items():
                per_metric.setdefault(name, []).append(float(value))

        aggregated: dict[str, float] = {}
        for name, values in per_metric.items():
            for agg in self.aggregations:
                key = f"{name}.{agg}"
                aggregated[key] = _aggregate(values, agg)
        return aggregated


def _aggregate(values: list[float], aggregation: str) -> float:
    if aggregation == "mean":
        return sum(values) / len(values)
    if aggregation == "min":
        return min(values)
    if aggregation == "max":
        return max(values)
    if aggregation == "sum":
        return sum(values)
    if aggregation == "std":
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return sqrt(variance)
    raise ValueError(f"unsupported aggregation: {aggregation}")
