"""Tests for canonical plotting helpers over sweep and optimization result objects."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from phys_sims_utils.harness.plotting import (
    plot_convergence_best_so_far,
    plot_metric_scatter,
    plot_objective_heatmap_2d,
    plot_objective_slice_1d,
)
from phys_sims_utils.shared import EvalResult, OptimizationHistory, SweepResult


def _configure_agg_backend() -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg", force=True)
    assert "agg" in matplotlib.get_backend().lower()


def _make_sweep_result() -> SweepResult:
    timestamp = datetime(2025, 1, 1, tzinfo=timezone(timedelta(0)))
    evaluations = (
        EvalResult(
            theta={"alpha": 0.0, "beta": 0.0},
            objective=5.0,
            metrics={"rmse": 2.0, "mae": 1.5},
            seed=1,
            timestamp=timestamp,
        ),
        EvalResult(
            theta={"alpha": 0.0, "beta": 1.0},
            objective=3.0,
            metrics={"rmse": 1.5, "mae": 1.2},
            seed=2,
            timestamp=timestamp,
        ),
        EvalResult(
            theta={"alpha": 1.0, "beta": 0.0},
            objective=4.0,
            metrics={"rmse": 1.7, "mae": 1.1},
            seed=3,
            timestamp=timestamp,
        ),
        EvalResult(
            theta={"alpha": 1.0, "beta": 1.0},
            objective=1.0,
            metrics={"rmse": 0.8, "mae": 0.6},
            seed=4,
            timestamp=timestamp,
        ),
    )
    return SweepResult(evaluations=evaluations, seed=7, parameter_space=("alpha", "beta"))


def test_sweep_plot_helpers_create_output_files(tmp_path: Path) -> None:
    _configure_agg_backend()
    sweep = _make_sweep_result()

    one_d_path = plot_objective_slice_1d(
        sweep,
        parameter="alpha",
        output_path=tmp_path / "objective_slice",
    )
    heatmap_path = plot_objective_heatmap_2d(
        sweep,
        x_parameter="alpha",
        y_parameter="beta",
        output_path=tmp_path / "objective_heatmap.png",
    )
    scatter_path = plot_metric_scatter(
        sweep,
        x_metric="rmse",
        y_metric="mae",
        output_path=tmp_path / "metric_scatter.png",
    )

    for output in (one_d_path, heatmap_path, scatter_path):
        assert output.exists()
        assert output.stat().st_size > 0


def test_optimization_convergence_plot_creates_output_file(tmp_path: Path) -> None:
    _configure_agg_backend()
    sweep = _make_sweep_result()
    history = OptimizationHistory(evaluations=sweep.evaluations, best=sweep.evaluations[-1], seed=9)

    output = plot_convergence_best_so_far(
        history,
        output_path=tmp_path / "convergence.png",
    )

    assert output.exists()
    assert output.stat().st_size > 0
