"""Plotting helpers for canonical harness and optimization outputs."""

from sim_utils.harness.core import ReportSpec
from sim_utils.harness.plotting.optimization_plots import plot_convergence_best_so_far
from sim_utils.harness.plotting.sweep_plots import (
    plot_metric_scatter,
    plot_objective_heatmap_2d,
    plot_objective_slice_1d,
)

__all__ = [
    "ReportSpec",
    "plot_convergence_best_so_far",
    "plot_metric_scatter",
    "plot_objective_heatmap_2d",
    "plot_objective_slice_1d",
]
