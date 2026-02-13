"""Type-focused contract tests for shared harness/ML models."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from phys_sims_utils.harness import (
    InMemoryTestHarness,
    MetricSpec,
    ReportSpec,
    SweepSpec,
)
from phys_sims_utils.harness.adapters import Adapter
from phys_sims_utils.ml import OptimizationRunner
from phys_sims_utils.ml.strategies import RandomSearchStrategy
from phys_sims_utils.shared import (
    Candidate,
    EvalResult,
    OptimizationHistory,
    SweepResult,
)


class _DummyAdapter(Adapter):
    def run(self, config: dict[str, float], seed: int) -> EvalResult:
        value = float(config["alpha"])
        return EvalResult(
            theta={"alpha": value},
            objective=value,
            metrics={"rmse": value + seed},
            seed=seed,
        )


def test_eval_result_round_trip_serialization() -> None:
    result = EvalResult(
        theta={"alpha": 1.0},
        objective=0.5,
        metrics={"rmse": 0.1},
        artifacts={"plot": "plot.png"},
        seed=7,
        config_hash="abc123",
        timestamp=datetime(2025, 1, 1, tzinfo=timezone(timedelta(0))),
        provenance={"version": "0.0.0"},
    )

    payload = result.to_dict()
    restored = EvalResult.from_dict(payload)

    assert restored == result


def test_collection_container_round_trip_serialization() -> None:
    result = EvalResult(theta={"alpha": 1.0}, objective=1.2, seed=4)
    sweep = SweepResult(evaluations=(result,), seed=4, parameter_space=("alpha",))
    history = OptimizationHistory(evaluations=(result,), best=result, seed=4)

    assert SweepResult.from_dict(sweep.to_dict()) == sweep
    assert OptimizationHistory.from_dict(history.to_dict()) == history


def test_harness_specs_and_in_memory_harness() -> None:
    harness = InMemoryTestHarness(name="test")
    spec = SweepSpec(parameters={"alpha": (1.0, 2.0)}, mode="grid")
    metric_specs = (MetricSpec(name="rmse", goal="min"),)
    report = ReportSpec(title="summary", include_metrics=("rmse",))

    results = harness.run_sweep(
        adapter=_DummyAdapter(),
        base_config={},
        sweep_spec=spec,
        metric_spec=metric_specs,
        seed=11,
    )

    assert report.title == "summary"
    assert [item.theta["alpha"] for item in results.evaluations] == [1.0, 2.0]
    assert [item.seed for item in results.evaluations] == [11, 12]


def test_optimizer_strategy_and_runner_consume_shared_types() -> None:
    strategy = RandomSearchStrategy(seed=3)
    candidate = strategy.ask()
    eval_result = EvalResult(theta=candidate.theta, objective=2.0, seed=3)

    strategy.tell(eval_result)

    runner = OptimizationRunner()
    runner.record(eval_result)

    assert isinstance(candidate, Candidate)
    assert strategy.result.best == eval_result
    assert runner.result.best == eval_result
