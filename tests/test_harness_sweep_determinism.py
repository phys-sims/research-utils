"""Determinism and sweep-contract tests for harness sampling and execution."""

from __future__ import annotations

from dataclasses import dataclass

from research_utils.harness import EvalResult, MetricSpec, ParameterRange, SweepSpec, TestHarness, sample_points


@dataclass
class DummyAdapter:
    """Simple deterministic adapter that echoes config-derived outputs."""

    def run(self, config: dict[str, float], seed: int) -> EvalResult:
        objective = float(config["x"] * 2.0 + config["y"])
        return EvalResult(
            objective=objective,
            metrics={"seed_metric": float(seed)},
            metadata={"adapter_seed": seed},
        )


def test_random_sampling_same_seed_same_points() -> None:
    spec = SweepSpec(
        parameters={"x": ParameterRange(0.0, 1.0), "y": ParameterRange(-1.0, 1.0)},
        mode="random",
        n_samples=5,
    )

    points_a = sample_points(spec, seed=7)
    points_b = sample_points(spec, seed=7)

    assert points_a == points_b


def test_random_sampling_requires_seed_unless_opt_out() -> None:
    spec = SweepSpec(parameters={"x": ParameterRange(0.0, 1.0)}, mode="random", n_samples=3)

    try:
        sample_points(spec, seed=None)
    except ValueError as exc:
        assert "seed is required" in str(exc)
    else:
        raise AssertionError("expected ValueError when seed is omitted")

    opted_out = SweepSpec(
        parameters={"x": ParameterRange(0.0, 1.0)},
        mode="grid",
        allow_unseeded=True,
    )
    sample_points(opted_out, seed=None)


def test_run_sweep_same_seed_same_ordered_results() -> None:
    harness = TestHarness(name="demo-harness")
    adapter = DummyAdapter()
    spec = SweepSpec(
        parameters={"x": ParameterRange(0.0, 1.0), "y": ParameterRange(1.0, 2.0)},
        mode="random",
        n_samples=4,
    )
    metric_spec = MetricSpec(metric_fns={"scaled": lambda result: result.objective * 0.5})

    first = harness.run_sweep(adapter, base_config={}, sweep_spec=spec, metric_spec=metric_spec, seed=11)
    second = harness.run_sweep(adapter, base_config={}, sweep_spec=spec, metric_spec=metric_spec, seed=11)

    first_pairs = [
        (item.parameters, item.objective, item.metadata["eval_seed"], item.metadata["eval_index"])
        for item in first.evaluations
    ]
    second_pairs = [
        (item.parameters, item.objective, item.metadata["eval_seed"], item.metadata["eval_index"])
        for item in second.evaluations
    ]

    assert first_pairs == second_pairs
    assert first.summary_metrics == second.summary_metrics
    assert first.metadata["seed"] == 11
    assert first.metadata["parameter_names"] == ("x", "y")


def test_grid_sampling_stable_parameter_order() -> None:
    spec = SweepSpec(
        parameters={"b": ParameterRange(0.0, 1.0), "a": ParameterRange(0.0, 1.0)},
        mode="grid",
        grid_points=2,
        allow_unseeded=True,
    )

    points = sample_points(spec, seed=None)

    assert list(points[0].keys()) == ["a", "b"]
    assert points == [
        {"a": 0.0, "b": 0.0},
        {"a": 0.0, "b": 1.0},
        {"a": 1.0, "b": 0.0},
        {"a": 1.0, "b": 1.0},
    ]

def test_sweep_result_save_csv(tmp_path) -> None:
    harness = TestHarness(name="save-test")
    adapter = DummyAdapter()
    spec = SweepSpec(
        parameters={"x": ParameterRange(0.0, 1.0), "y": ParameterRange(1.0, 2.0)},
        mode="grid",
        grid_points=2,
        allow_unseeded=True,
    )
    result = harness.run_sweep(
        adapter,
        base_config={},
        sweep_spec=spec,
        metric_spec=MetricSpec(),
        seed=None,
    )

    out_path = result.save(tmp_path / "sweep.csv")

    assert out_path.exists()
    content = out_path.read_text(encoding="utf-8")
    assert "objective" in content
    assert "param.x" in content
