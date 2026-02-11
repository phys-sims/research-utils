"""Metric computation and aggregation helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Callable, Mapping

from research_utils.shared import EvalResult

MetricFn = Callable[[EvalResult], float]
AggregatorFn = Callable[[list[float]], float]


@dataclass(frozen=True)
class MetricSpec:
    """Metric declaration with deterministic reducer selection."""

    name: str
    goal: str = "min"
    compute: MetricFn | None = None
    aggregate: str = "mean"


def compute_metrics(result: EvalResult, specs: tuple[MetricSpec, ...]) -> dict[str, float]:
    """Compute metrics for one evaluation by reading stored values or callback output."""
    computed: dict[str, float] = {}
    for spec in specs:
        if spec.compute is not None:
            computed[spec.name] = float(spec.compute(result))
            continue
        if spec.name in result.metrics:
            computed[spec.name] = float(result.metrics[spec.name])
    return computed


def aggregate_metrics(
    evaluations: tuple[EvalResult, ...], specs: tuple[MetricSpec, ...]
) -> dict[str, float]:
    """Aggregate metric values across evaluations in stable order."""
    by_name: dict[str, list[float]] = {spec.name: [] for spec in specs}

    for evaluation in evaluations:
        values = compute_metrics(evaluation, specs)
        for spec in specs:
            if spec.name in values:
                by_name[spec.name].append(values[spec.name])

    aggregates: dict[str, float] = {}
    for spec in specs:
        metric_values = by_name[spec.name]
        if not metric_values:
            continue
        reducer = _resolve_aggregator(spec.aggregate)
        aggregates[spec.name] = reducer(metric_values)
    return aggregates


def _resolve_aggregator(name: str) -> AggregatorFn:
    normalized = name.lower()
    if normalized == "mean":
        return lambda values: float(mean(values))
    if normalized == "min":
        return lambda values: float(min(values))
    if normalized == "max":
        return lambda values: float(max(values))
    msg = f"unsupported metric aggregator: {name}"
    raise ValueError(msg)


@dataclass(frozen=True)
class MetricSummary:
    """Aggregated metric view for a completed sweep."""

    values: Mapping[str, float] = field(default_factory=dict)


__all__ = ["MetricSpec", "MetricSummary", "aggregate_metrics", "compute_metrics"]
