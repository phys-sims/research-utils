"""Optimization runner and strategy behavior tests."""

from __future__ import annotations

import json
from pathlib import Path

from research_utils.ml import OptimizationLogger, OptimizationRunner, Parameter, ParameterSpace
from research_utils.ml.strategies import RandomStrategy
from research_utils.shared import EvalResult


def _quadratic_objective(theta: dict[str, float], seed: int) -> EvalResult:
    x = theta["x"]
    objective = (x - 0.25) ** 2
    return EvalResult(theta=dict(theta), objective=objective, seed=seed)


def test_random_strategy_is_reproducible_for_same_seed() -> None:
    parameter_space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))

    strategy_a = RandomStrategy(parameter_space=parameter_space, seed=7)
    strategy_b = RandomStrategy(parameter_space=parameter_space, seed=7)

    asked_a = [strategy_a.ask().theta for _ in range(4)]
    asked_b = [strategy_b.ask().theta for _ in range(4)]

    assert asked_a == asked_b


def test_runner_tracks_best_point_with_batching() -> None:
    parameter_space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))
    strategy = RandomStrategy(parameter_space=parameter_space, seed=11)
    runner = OptimizationRunner(strategy=strategy, evaluator=_quadratic_objective, seed=101)

    result = runner.run(iterations=8, batch_size=3)

    assert len(result.evaluations) == 8
    assert result.best is not None
    assert result.best.objective == min(item.objective for item in result.evaluations)


def test_runner_maps_exceptions_to_penalty() -> None:
    parameter_space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))

    def flaky(theta: dict[str, float], seed: int) -> EvalResult:
        if seed % 2 == 0:
            msg = "simulated failure"
            raise RuntimeError(msg)
        return EvalResult(theta=dict(theta), objective=0.1, seed=seed)

    strategy = RandomStrategy(parameter_space=parameter_space, seed=3)
    runner = OptimizationRunner(
        strategy=strategy,
        evaluator=flaky,
        seed=10,
        penalty_objective=999.0,
    )

    result = runner.run(iterations=4)

    penalties = [item for item in result.evaluations if item.objective == 999.0]
    assert len(penalties) == 2
    assert all(item.metrics.get("penalty") == 1.0 for item in penalties)
    assert all(item.artifacts.get("error_type") == "RuntimeError" for item in penalties)


def test_logger_writes_jsonl_csv_and_best_snapshots(tmp_path: Path) -> None:
    parameter_space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))
    logger = OptimizationLogger(
        output_dir=tmp_path,
        run_name="unit",
        run_metadata={"seed": 4, "strategy": "random"},
    )
    runner = OptimizationRunner(
        strategy=RandomStrategy(parameter_space=parameter_space, seed=4),
        evaluator=_quadratic_objective,
        seed=4,
        logger=logger,
    )

    result = runner.run(iterations=5)

    assert result.best is not None
    metadata = json.loads((tmp_path / "unit.metadata.json").read_text(encoding="utf-8"))
    assert metadata == {"seed": 4, "strategy": "random"}

    jsonl_lines = (tmp_path / "unit.jsonl").read_text(encoding="utf-8").strip().splitlines()
    csv_lines = (tmp_path / "unit.csv").read_text(encoding="utf-8").strip().splitlines()
    best_lines = (tmp_path / "unit.best.jsonl").read_text(encoding="utf-8").strip().splitlines()

    assert len(jsonl_lines) == 5
    assert len(csv_lines) == 6
    assert len(best_lines) >= 1
