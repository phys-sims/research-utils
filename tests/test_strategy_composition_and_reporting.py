"""Composition strategy and summary artifact tests."""

from __future__ import annotations

import json
from pathlib import Path

from phys_sims_utils.harness import build_optimization_summary, build_sweep_summary, save_summary
from phys_sims_utils.ml.strategies import PortfolioStrategy, RandomStrategy, StagedStrategy
from phys_sims_utils.shared import EvalResult, OptimizationHistory, SweepResult


def _result(value: float, *, seed: int) -> EvalResult:
    return EvalResult(theta={"x": value}, objective=value, seed=seed)


def test_staged_strategy_advances_by_stage_limits() -> None:
    first = RandomStrategy(seed=1, max_iterations=100)
    second = RandomStrategy(seed=2, max_iterations=100)
    strategy = StagedStrategy(stages=(first, second), stage_max_iterations=(2, 2))

    asked = [strategy.ask() for _ in range(4)]
    for index, candidate in enumerate(asked):
        strategy.tell(_result(float(candidate.theta["x"]), seed=index))

    assert len(first.result.evaluations) == 2
    assert len(second.result.evaluations) == 2
    assert len(strategy.result.evaluations) == 4


def test_portfolio_strategy_round_robin_dispatch() -> None:
    left = RandomStrategy(seed=10, max_iterations=2)
    right = RandomStrategy(seed=11, max_iterations=2)
    portfolio = PortfolioStrategy(strategies=(left, right))

    for idx in range(4):
        candidate = portfolio.ask()
        portfolio.tell(_result(float(candidate.theta["x"]), seed=idx))

    assert len(left.result.evaluations) == 2
    assert len(right.result.evaluations) == 2
    assert portfolio.is_converged


def test_summary_artifacts_are_stable(tmp_path: Path) -> None:
    sweep = SweepResult(
        evaluations=(
            EvalResult(theta={"x": 0.0}, objective=4.0, metrics={"rmse": 2.0}, seed=3),
            EvalResult(theta={"x": 1.0}, objective=1.0, metrics={"rmse": 1.0}, seed=4),
        ),
        seed=3,
        parameter_space=("x",),
        config_hash="abc123",
        provenance={"harness": "default"},
    )
    optimization = OptimizationHistory(
        evaluations=(
            EvalResult(theta={"x": 0.5}, objective=0.25, seed=5),
            EvalResult(theta={"x": 0.2}, objective=0.04, seed=6),
        ),
        best=EvalResult(theta={"x": 0.2}, objective=0.04, seed=6),
        seed=5,
        parameter_space=("x",),
        config_hash="def456",
        provenance={"strategy": "random"},
    )

    sweep_summary = build_sweep_summary(sweep)
    opt_summary = build_optimization_summary(optimization)

    sweep_path = save_summary(sweep_summary, tmp_path / "sweep.summary.json")
    opt_path = save_summary(opt_summary, tmp_path / "optimization.summary.json")

    sweep_payload = json.loads(sweep_path.read_text(encoding="utf-8"))
    opt_payload = json.loads(opt_path.read_text(encoding="utf-8"))

    assert sweep_payload["run_type"] == "sweep"
    assert sweep_payload["objective"] == {"min": 1.0, "max": 4.0, "mean": 2.5}
    assert sweep_payload["metrics_present"] == ["rmse"]
    assert sweep_payload["structure_keys"] == []
    assert sweep_payload["structure_values"] == {}

    assert opt_payload["run_type"] == "optimization"
    assert opt_payload["objective"] == {"min": 0.04, "max": 0.25, "mean": 0.145}
    assert opt_payload["best"]["objective"] == 0.04
    assert opt_payload["structure_keys"] == []
    assert opt_payload["structure_values"] == {}


def test_summary_artifacts_capture_structure_metadata() -> None:
    optimization = OptimizationHistory(
        evaluations=(
            EvalResult(theta={"x": 0.1, "lens": "convex", "enabled": True}, objective=0.4, seed=1),
            EvalResult(
                theta={"x": 0.2, "lens": "concave", "enabled": False},
                objective=0.3,
                seed=2,
            ),
        ),
        seed=1,
    )

    summary = build_optimization_summary(optimization)

    assert summary["structure_keys"] == ["enabled", "lens"]
    assert summary["structure_values"] == {"enabled": [False, True], "lens": ["concave", "convex"]}


def test_optimization_runner_is_deterministic_for_mixed_parameter_topology() -> None:
    from phys_sims_utils.ml import OptimizationRunner, Parameter, ParameterSpace

    parameter_space = ParameterSpace(
        parameters=(
            Parameter(name="x", bounds=(0.0, 1.0)),
            Parameter(name="lens", choices=("convex", "concave")),
            Parameter(name="enabled", choices=(False, True)),
        )
    )

    def objective(theta: dict[str, float | int | str | bool], seed: int) -> EvalResult:
        lens = 0.0 if theta["lens"] == "convex" else 0.1
        enabled = 0.0 if theta["enabled"] else 0.2
        x = float(theta["x"])
        return EvalResult(theta=theta, objective=x + lens + enabled, seed=seed)

    run_a = OptimizationRunner(
        strategy=RandomStrategy(parameter_space=parameter_space, seed=7),
        evaluator=objective,
        seed=100,
    ).run(iterations=5)
    run_b = OptimizationRunner(
        strategy=RandomStrategy(parameter_space=parameter_space, seed=7),
        evaluator=objective,
        seed=100,
    ).run(iterations=5)

    assert [item.theta for item in run_a.evaluations] == [item.theta for item in run_b.evaluations]
    assert [item.objective for item in run_a.evaluations] == [
        item.objective for item in run_b.evaluations
    ]
    assert run_a.best is not None
    assert run_b.best is not None
    assert run_a.best.theta == run_b.best.theta
    assert run_a.best.objective == run_b.best.objective
