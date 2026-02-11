"""Tests for the optional phys-pipeline harness adapter."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from unittest import mock

import research_utils.harness.adapters.phys_pipeline as phys_adapter_module
from research_utils.harness.adapters.phys_pipeline import PhysPipelineAdapter


class _DummyPipeline:
    def __init__(self, *, seed_bias: int = 0) -> None:
        self.seed_bias = seed_bias

    def run(self, config: Mapping[str, Any], seed: int) -> Mapping[str, Any]:
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
        pipeline=lambda seed: _DummyPipeline(seed_bias=int(seed)),
        objective_key="objective",
        metric_extractors={
            "rmse": lambda output: float(output["rmse"]),
            "throughput": lambda output: 1000.0 / float(output["latency_ms"]),
        },
    )

    result = adapter.run(config={"alpha": 1.0, "beta": 0.4}, seed=3)

    assert result.objective == 16.4
    assert result.metrics["rmse"] == 0.6
    assert abs(result.metrics["throughput"] - 121.95121951219512) < 1e-12


def test_adapter_missing_objective_key_raises_clear_error() -> None:
    adapter = PhysPipelineAdapter(
        pipeline=_DummyPipeline(),
        objective_key="missing_key",
    )

    try:
        adapter.run(config={"alpha": 1.0}, seed=1)
    except KeyError as exc:
        assert "missing_key" in str(exc)
    else:  # pragma: no cover - defensive branch for explicit failure signal
        msg = "Expected KeyError for missing objective key"
        raise AssertionError(msg)


def test_adapter_default_pipeline_missing_optional_dependency_raises_clear_error() -> None:
    def _failing_import(name: str) -> Any:
        raise ImportError(f"No module named '{name}'")

    adapter = PhysPipelineAdapter(objective_key="objective")
    with mock.patch.object(phys_adapter_module, "import_module", _failing_import):
        try:
            adapter.run(config={"alpha": 1.0}, seed=1)
        except ImportError as exc:
            assert "requires optional dependency 'phys-pipeline'" in str(exc)
        else:  # pragma: no cover - defensive branch for explicit failure signal
            msg = "Expected ImportError for missing phys-pipeline"
            raise AssertionError(msg)
