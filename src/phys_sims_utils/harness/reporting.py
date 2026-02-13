"""Canonical deterministic reporting helpers for sweep and optimization artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from phys_sims_utils.shared import OptimizationHistory, SweepResult


def build_sweep_summary(result: SweepResult) -> dict[str, Any]:
    """Build a stable summary artifact for a sweep run."""
    objectives = [evaluation.objective for evaluation in result.evaluations]
    metric_keys = sorted(
        {
            key
            for evaluation in result.evaluations
            for key in evaluation.metrics
        }
    )
    structure_values = _collect_structure_values(
        [evaluation.theta for evaluation in result.evaluations]
    )

    return {
        "run_type": "sweep",
        "seed": result.seed,
        "num_evaluations": len(result.evaluations),
        "parameter_space": list(result.parameter_space),
        "config_hash": result.config_hash,
        "provenance": dict(result.provenance),
        "objective": {
            "min": min(objectives) if objectives else None,
            "max": max(objectives) if objectives else None,
            "mean": (sum(objectives) / len(objectives)) if objectives else None,
        },
        "metrics_present": metric_keys,
        "structure_keys": sorted(structure_values),
        "structure_values": structure_values,
    }


def build_optimization_summary(history: OptimizationHistory) -> dict[str, Any]:
    """Build a stable summary artifact for an optimization run."""
    objectives = [evaluation.objective for evaluation in history.evaluations]
    best = history.best
    structure_values = _collect_structure_values(
        [evaluation.theta for evaluation in history.evaluations]
    )

    return {
        "run_type": "optimization",
        "seed": history.seed,
        "num_evaluations": len(history.evaluations),
        "parameter_space": list(history.parameter_space),
        "config_hash": history.config_hash,
        "provenance": dict(history.provenance),
        "objective": {
            "min": min(objectives) if objectives else None,
            "max": max(objectives) if objectives else None,
            "mean": (sum(objectives) / len(objectives)) if objectives else None,
        },
        "best": best.to_dict() if best is not None else None,
        "structure_keys": sorted(structure_values),
        "structure_values": structure_values,
    }


def _collect_structure_values(thetas: list[dict[str, Any]]) -> dict[str, list[Any]]:
    grouped: dict[str, set[Any]] = {}
    for theta in thetas:
        for key, value in theta.items():
            if isinstance(value, float):
                continue
            grouped.setdefault(key, set()).add(value)
    return {key: sorted(values, key=str) for key, values in sorted(grouped.items())}


def save_summary(summary: dict[str, Any], path: str | Path) -> Path:
    """Persist a summary artifact as deterministic JSON."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(summary, sort_keys=True, indent=2), encoding="utf-8")
    return destination


__all__ = [
    "build_optimization_summary",
    "build_sweep_summary",
    "save_summary",
]
