"""Core harness contracts and deterministic sweep execution."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from sim_utils.harness.adapters import Adapter
from sim_utils.harness.metrics import (
    MetricSpec,
    aggregate_metrics,
    compute_metrics,
)
from sim_utils.harness.sweep import SweepSpec
from sim_utils.shared import EvalResult, SweepResult


@dataclass(frozen=True)
class ReportSpec:
    """Report generation configuration for canonical harness outputs."""

    title: str = "report"
    include_metrics: tuple[str, ...] = ()


class TestHarness(Protocol):
    __test__: bool = False

    """Protocol for adapter-backed harness implementations."""

    name: str

    def run_sweep(
        self,
        adapter: Adapter,
        base_config: dict[str, Any],
        sweep_spec: SweepSpec,
        metric_spec: tuple[MetricSpec, ...],
        seed: int | None,
    ) -> SweepResult:
        """Run a deterministic sweep and return canonical results."""


@dataclass
class InMemoryTestHarness:
    """Minimal deterministic harness implementation for tests and examples."""

    name: str = "default"
    allow_unseeded: bool = False
    _results: list[EvalResult] = field(default_factory=list)

    def run_sweep(
        self,
        adapter: Adapter,
        base_config: dict[str, Any],
        sweep_spec: SweepSpec,
        metric_spec: tuple[MetricSpec, ...] = (),
        seed: int | None = None,
    ) -> SweepResult:
        run_seed = _resolve_seed(seed, allow_unseeded=self.allow_unseeded)
        points = sweep_spec.sample(seed=run_seed)
        base_hash = _hash_payload(base_config)

        evaluations: list[EvalResult] = []
        for index, point in enumerate(points):
            config = dict(base_config)
            config.update(point)
            eval_seed = _derive_seed(run_seed, index)
            result = adapter.run(config=config, seed=eval_seed)

            metrics = dict(result.metrics)
            metrics.update(compute_metrics(result, metric_spec))

            provenance = dict(result.provenance)
            provenance.update(
                {
                    "harness": self.name,
                    "sampling_mode": sweep_spec.mode,
                    "sweep_index": str(index),
                }
            )

            evaluations.append(
                EvalResult(
                    theta=dict(point),
                    objective=float(result.objective),
                    metrics=metrics,
                    artifacts=dict(result.artifacts),
                    seed=eval_seed,
                    config_hash=base_hash,
                    timestamp=result.timestamp,
                    provenance=provenance,
                )
            )

        self._results = evaluations
        evaluation_tuple = tuple(evaluations)
        aggregate = aggregate_metrics(evaluation_tuple, metric_spec)
        parameter_space = tuple(sorted(sweep_spec.parameters.keys()))
        sweep_provenance = {
            "harness": self.name,
            "sampling_mode": sweep_spec.mode,
            "metric_aggregate": json.dumps(aggregate, sort_keys=True),
        }

        return SweepResult(
            evaluations=evaluation_tuple,
            seed=run_seed,
            parameter_space=parameter_space,
            config_hash=base_hash,
            provenance=sweep_provenance,
        )


def _resolve_seed(seed: int | None, *, allow_unseeded: bool) -> int:
    if seed is None and not allow_unseeded:
        msg = "seed is required unless allow_unseeded=True"
        raise ValueError(msg)
    return int(seed or 0)


def _hash_payload(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _derive_seed(seed: int, index: int) -> int:
    # Simple explicit derivation that keeps ordering deterministic.
    return seed + index


__all__ = [
    "InMemoryTestHarness",
    "MetricSpec",
    "ReportSpec",
    "SweepSpec",
    "TestHarness",
]
