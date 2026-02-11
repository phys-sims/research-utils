"""Tests for the optional phys-pipeline harness adapter."""

from __future__ import annotations

from typing import Any

import pytest

from research_utils.harness.adapters.phys_pipeline import PhysPipelineAdapter


class _DummyPipeline:
    def __init__(self, *, seed_bias: int = 0) -> None:
        self.seed_bias = seed_bias

    def run(self, config: dict[str, Any], seed: int) -> dict[str, float]:
        alpha = float(config["alpha"])
        beta = float(config.get("beta", 0.0))
        objective = alpha * 10.0 + beta + float(seed + self.seed_bias)
        return {
            "objective": objective,
            "rmse": abs(alpha - beta),
            "latency_ms": objective / 2.0,
        }


def test_adapter_respects_seed_deterministically() -> None:
    adapter = PhysPipelineAdapter(pipeline=_DummyPipeline(), objective_key="objective")

    config = {"alpha": 0.2, "beta": 0.1}
    first = adapter.run(config=config, seed=41)
    second = adapter.run(config=config, seed=41)
    changed_seed = adapter.run(config=config, seed=42)

    assert first.objective == second.objective
    assert first.seed == second.seed == 41
    assert changed_seed.objective != first.objective


def test_adapter_extracts_objective_key() -> None:
    adapter = PhysPipelineAdapter(pipeline=_DummyPipeline(), objective_key="objective")

    result = adapter.run(config={"alpha": 0.5, "beta": 0.2}, seed=7)

    assert result.objective == 12.2
    assert result.theta == {"alpha": 0.5, "beta": 0.2}


def test_adapter_extracts_additional_metrics() -> None:
    adapter = PhysPipelineAdapter(
        pipeline=lambda seed: _DummyPipeline(seed_bias=seed),
        objective_key="objective",
        metric_extractors={
            "rmse": lambda output: float(output["rmse"]),
            "throughput": lambda output: 1000.0 / float(output["latency_ms"]),
        },
    )

    result = adapter.run(config={"alpha": 1.0, "beta": 0.4}, seed=3)

    assert result.objective == 16.4
    assert result.metrics["rmse"] == 0.6
    assert result.metrics["throughput"] == pytest.approx(121.95121951219512)
