"""Tests for adapter-backed simulation evaluator."""

from __future__ import annotations

from typing import Any

from research_utils.harness.adapters import Adapter
from research_utils.ml import SimulationEvaluator
from research_utils.shared import EvalResult


class _DummyAdapter(Adapter):
    def run(self, config: dict[str, Any], seed: int) -> EvalResult:
        value = config["alpha"]
        return EvalResult(theta=config, objective=value * 2.0, metrics={"m": value}, seed=seed)


def test_simulation_evaluator_exposes_objective_and_metrics() -> None:
    evaluator = SimulationEvaluator(adapter=_DummyAdapter())

    objective, metrics = evaluator.objective_and_metrics({"alpha": 2.5}, seed=9)

    assert objective == 5.0
    assert metrics == {"m": 2.5}
