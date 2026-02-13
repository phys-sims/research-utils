"""End-to-end dummy simulation example for adapter, harness, plotting, and optimization."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from phys_sims_utils.harness import InMemoryTestHarness, SweepSpec
from phys_sims_utils.harness.adapters.phys_pipeline import PhysPipelineAdapter
from phys_sims_utils.harness.plotting import (
    plot_convergence_best_so_far,
    plot_metric_scatter,
    plot_objective_heatmap_2d,
)
from phys_sims_utils.ml import OptimizationLogger, OptimizationRunner, Parameter, ParameterSpace
from phys_sims_utils.ml.evaluator import SimulationEvaluator
from phys_sims_utils.ml.strategies import RandomStrategy


class DummyPipeline:
    """Simple deterministic stand-in for an external simulation pipeline."""

    def run(self, config: Mapping[str, Any], seed: int) -> Mapping[str, Any]:
        alpha = float(config["alpha"])
        beta = float(config["beta"])
        target_a = 0.35
        target_b = 0.75

        objective = (alpha - target_a) ** 2 + (beta - target_b) ** 2
        rmse = objective**0.5
        mae = (abs(alpha - target_a) + abs(beta - target_b)) / 2.0
        return {
            "objective": objective,
            "rmse": rmse,
            "mae": mae,
            "seed_echo": float(seed),
        }


def run_example(output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    adapter = PhysPipelineAdapter(
        pipeline=DummyPipeline(),
        objective_key="objective",
        metric_extractors={
            "rmse": lambda output: float(output["rmse"]),
            "mae": lambda output: float(output["mae"]),
        },
    )

    harness = InMemoryTestHarness(name="dummy-e2e")
    sweep_spec = SweepSpec(
        parameters={
            "alpha": (0.1, 0.3, 0.5),
            "beta": (0.2, 0.6, 1.0),
        },
        mode="grid",
    )

    sweep_result = harness.run_sweep(
        adapter=adapter,
        base_config={},
        sweep_spec=sweep_spec,
        seed=21,
    )

    sweep_table_path = sweep_result.save(output_dir / "sweep_results.csv")
    heatmap_path = plot_objective_heatmap_2d(
        sweep_result,
        x_parameter="alpha",
        y_parameter="beta",
        output_path=output_dir / "objective_heatmap.png",
    )
    metric_scatter_path = plot_metric_scatter(
        sweep_result,
        x_metric="rmse",
        y_metric="mae",
        output_path=output_dir / "metric_scatter.png",
    )

    parameter_space = ParameterSpace(
        parameters=(
            Parameter(name="alpha", bounds=(0.1, 0.5)),
            Parameter(name="beta", bounds=(0.2, 1.0)),
        )
    )
    optimizer = RandomStrategy(parameter_space=parameter_space, seed=21)
    logger = OptimizationLogger(
        output_dir=output_dir,
        run_name="dummy_optimization",
        run_metadata={
            "seed": 21,
            "strategy": "random",
            "adapter": "PhysPipelineAdapter(DummyPipeline)",
        },
    )
    runner = OptimizationRunner(
        strategy=optimizer,
        evaluator=SimulationEvaluator(adapter=adapter),
        seed=21,
        logger=logger,
    )

    history = runner.run(iterations=8, batch_size=2)
    convergence_path = plot_convergence_best_so_far(
        history,
        output_path=output_dir / "optimization_convergence.png",
    )

    metadata_path = output_dir / "run_metadata.json"
    metadata_payload = {
        "seed": 21,
        "sweep_size": len(sweep_result.evaluations),
        "optimization_evaluations": len(history.evaluations),
        "best_objective": history.best.objective if history.best is not None else None,
        "sweep_config_hash": sweep_result.config_hash,
        "sweep_provenance": sweep_result.provenance,
    }
    metadata_json = json.dumps(metadata_payload, sort_keys=True, indent=2)
    metadata_path.write_text(metadata_json, encoding="utf-8")

    return {
        "sweep_table": sweep_table_path,
        "heatmap": heatmap_path,
        "metric_scatter": metric_scatter_path,
        "convergence": convergence_path,
        "metadata": metadata_path,
        "optimizer_metadata": output_dir / "dummy_optimization.metadata.json",
    }


if __name__ == "__main__":
    artifacts = run_example(Path("artifacts/dummy_end_to_end"))
    for name, path in artifacts.items():
        print(f"{name}: {path}")
