"""Plotting helpers for optimization history outputs."""

from __future__ import annotations

from pathlib import Path

from phys_sims_utils.harness.plotting.common import create_figure, finalize_figure
from phys_sims_utils.shared import OptimizationHistory


def plot_convergence_best_so_far(
    history: OptimizationHistory,
    *,
    output_path: str | Path,
    dpi: int = 150,
) -> Path:
    """Plot best-so-far objective against evaluation count."""
    if not history.evaluations:
        msg = "optimization history must include at least one evaluation"
        raise ValueError(msg)

    best_values: list[float] = []
    current_best = float("inf")
    for evaluation in history.evaluations:
        current_best = min(current_best, float(evaluation.objective))
        best_values.append(current_best)

    eval_counts = list(range(1, len(best_values) + 1))

    fig, ax = create_figure()
    ax.plot(eval_counts, best_values, marker="o", linewidth=1.5)
    ax.set_xlabel("evaluation")
    ax.set_ylabel("best objective so far")
    ax.set_title("Optimization convergence")
    ax.grid(alpha=0.3)

    return finalize_figure(fig, output_path, dpi=dpi)


__all__ = ["plot_convergence_best_so_far"]
