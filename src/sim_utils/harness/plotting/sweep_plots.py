"""Canonical plotting helpers for :class:`~sim_utils.shared.SweepResult`."""

from __future__ import annotations

from pathlib import Path

from sim_utils.harness.plotting.common import (
    create_figure,
    finalize_figure,
    require_matplotlib,
)
from sim_utils.shared import SweepResult


def plot_objective_slice_1d(
    sweep: SweepResult,
    *,
    parameter: str,
    output_path: str | Path,
    dpi: int = 150,
) -> Path:
    """Plot objective values against a single parameter from sweep evaluations."""
    points = sorted(
        (
            evaluation.theta[parameter],
            evaluation.objective,
        )
        for evaluation in sweep.evaluations
        if parameter in evaluation.theta
    )
    if not points:
        msg = f"parameter '{parameter}' not found in sweep evaluations"
        raise ValueError(msg)

    x_values = [float(value) for value, _ in points]
    y_values = [float(value) for _, value in points]

    fig, ax = create_figure()
    ax.plot(x_values, y_values, marker="o", linewidth=1.5)
    ax.set_xlabel(parameter)
    ax.set_ylabel("objective")
    ax.set_title(f"Objective slice: {parameter}")
    ax.grid(alpha=0.3)

    return finalize_figure(fig, output_path, dpi=dpi)


def plot_objective_heatmap_2d(
    sweep: SweepResult,
    *,
    x_parameter: str,
    y_parameter: str,
    output_path: str | Path,
    dpi: int = 150,
) -> Path:
    """Plot a 2D objective heatmap using two sweep parameters."""
    triples = [
        (
            float(evaluation.theta[x_parameter]),
            float(evaluation.theta[y_parameter]),
            float(evaluation.objective),
        )
        for evaluation in sweep.evaluations
        if x_parameter in evaluation.theta and y_parameter in evaluation.theta
    ]
    if not triples:
        msg = (
            f"parameters '{x_parameter}' and '{y_parameter}' must both be present "
            "in sweep evaluations"
        )
        raise ValueError(msg)

    plt = require_matplotlib()
    fig, ax = create_figure(figsize=(6.5, 5.2))
    x_values = [row[0] for row in triples]
    y_values = [row[1] for row in triples]
    objectives = [row[2] for row in triples]

    mesh = ax.tricontourf(x_values, y_values, objectives, levels=16, cmap="viridis")
    ax.scatter(x_values, y_values, c="white", edgecolors="black", s=20, linewidths=0.3)
    ax.set_xlabel(x_parameter)
    ax.set_ylabel(y_parameter)
    ax.set_title(f"Objective heatmap: {x_parameter} vs {y_parameter}")
    colorbar = fig.colorbar(mesh, ax=ax)
    colorbar.set_label("objective")
    ax.grid(alpha=0.2)
    plt.tight_layout()

    return finalize_figure(fig, output_path, dpi=dpi)


def plot_metric_scatter(
    sweep: SweepResult,
    *,
    x_metric: str,
    y_metric: str,
    output_path: str | Path,
    dpi: int = 150,
) -> Path:
    """Scatter plot of two metrics, colored by objective."""
    rows = [
        (
            float(evaluation.metrics[x_metric]),
            float(evaluation.metrics[y_metric]),
            float(evaluation.objective),
        )
        for evaluation in sweep.evaluations
        if x_metric in evaluation.metrics and y_metric in evaluation.metrics
    ]
    if not rows:
        msg = f"metrics '{x_metric}' and '{y_metric}' not found in sweep evaluations"
        raise ValueError(msg)

    fig, ax = create_figure()
    x_values = [item[0] for item in rows]
    y_values = [item[1] for item in rows]
    objectives = [item[2] for item in rows]

    scatter = ax.scatter(
        x_values,
        y_values,
        c=objectives,
        cmap="viridis",
        s=35,
        edgecolors="black",
        linewidths=0.25,
    )
    ax.set_xlabel(x_metric)
    ax.set_ylabel(y_metric)
    ax.set_title(f"Metric scatter: {x_metric} vs {y_metric}")
    ax.grid(alpha=0.3)
    colorbar = fig.colorbar(scatter, ax=ax)
    colorbar.set_label("objective")

    return finalize_figure(fig, output_path, dpi=dpi)


__all__ = [
    "plot_metric_scatter",
    "plot_objective_heatmap_2d",
    "plot_objective_slice_1d",
]
