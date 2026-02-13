from __future__ import annotations

from pathlib import Path

from phys_sims_utils.harness import InMemoryTestHarness, SweepSpec
from phys_sims_utils.harness.adapters import Adapter
from phys_sims_utils.shared import EvalResult


class QuadraticAdapter(Adapter):
    def run(self, config: dict[str, float], seed: int) -> EvalResult:
        x = float(config["x"])
        y = float(config["y"])
        objective = x * x + y * y
        return EvalResult(
            theta={"x": x, "y": y},
            objective=objective,
            metrics={"sum": x + y},
            seed=seed,
            provenance={"adapter": "quadratic"},
        )


def test_random_sampling_same_seed_same_points_and_order() -> None:
    spec = SweepSpec(
        parameters={"x": (0.0, 1.0), "y": (10.0, 20.0)},
        mode="random",
        num_samples=5,
    )

    a = spec.sample(seed=123)
    b = spec.sample(seed=123)

    assert a == b


def test_run_sweep_same_seed_same_ordered_results() -> None:
    harness = InMemoryTestHarness(name="determinism")
    spec = SweepSpec(
        parameters={"x": (0.0, 1.0), "y": (10.0, 20.0)},
        mode="random",
        num_samples=4,
    )

    run_a = harness.run_sweep(QuadraticAdapter(), {}, spec, metric_spec=(), seed=9)
    run_b = harness.run_sweep(QuadraticAdapter(), {}, spec, metric_spec=(), seed=9)

    assert [result.theta for result in run_a.evaluations] == [
        result.theta for result in run_b.evaluations
    ]
    assert [result.objective for result in run_a.evaluations] == [
        result.objective for result in run_b.evaluations
    ]
    assert [result.seed for result in run_a.evaluations] == [
        result.seed for result in run_b.evaluations
    ]


def test_sweep_result_save_csv(tmp_path: Path) -> None:
    harness = InMemoryTestHarness(name="save")
    spec = SweepSpec(parameters={"x": (0.0, 1.0), "y": (0.0, 1.0)}, mode="grid")
    result = harness.run_sweep(QuadraticAdapter(), {}, spec, metric_spec=(), seed=5)

    destination = result.save(tmp_path / "result.csv")

    assert destination.exists()
    text = destination.read_text(encoding="utf-8")
    assert "objective" in text
    assert "theta.x" in text
