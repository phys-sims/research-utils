"""v1.2 agent workflow contract and determinism tests."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from phys_sims_utils.agents import (
    AdaptationAssistantRequest,
    AgentWorkflowError,
    GraphicsConciergeRequest,
    GraphicsIntent,
    StrategyAdvisorRequest,
    advise_optimization_strategy,
    generate_experiment_script,
    run_adaptation_assistant,
    run_graphics_concierge,
)
from phys_sims_utils.agents.experiment_gen import ExperimentScriptSpec, ScriptProvenance
from phys_sims_utils.shared import EvalResult, OptimizationHistory, SweepResult


def test_adaptation_assistant_is_deterministic(tmp_path: Path) -> None:
    scripts_dir = tmp_path / "project" / "scripts"
    scripts_dir.mkdir(parents=True)

    spec = ExperimentScriptSpec(
        name="valid",
        adapter_import="some_pkg.adapter",
        parameter_paths=("physics.alpha",),
        base_config={"physics": {"alpha": 1.0}},
        structure_fields=("physics.include_lens",),
    )
    generate_experiment_script(
        spec,
        output_dir=scripts_dir,
        generated_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        provenance=ScriptProvenance(package_version="0.4.0", git_commit="abc"),
    )

    request = AdaptationAssistantRequest(
        project_root=(tmp_path / "project").as_posix(),
        output_dir=(tmp_path / "out_a").as_posix(),
        valid_parameter_paths=("physics.alpha",),
        seed=1,
        config_hash="cfg",
        provenance={"tool": "test"},
    )

    response_a = run_adaptation_assistant(request)
    response_b = run_adaptation_assistant(
        AdaptationAssistantRequest(
            project_root=request.project_root,
            output_dir=(tmp_path / "out_b").as_posix(),
            valid_parameter_paths=request.valid_parameter_paths,
            seed=1,
            config_hash="cfg",
            provenance={"tool": "test"},
        )
    )

    assert response_a.findings == response_b.findings
    assert response_a.checklist == response_b.checklist


def test_strategy_advisor_contract_and_fallbacks(tmp_path: Path) -> None:
    response = advise_optimization_strategy(
        StrategyAdvisorRequest(
            budget=80,
            has_categorical_parameters=False,
            scipy_available=True,
            cma_available=True,
            seed=5,
            config_hash="cfg-1",
        ),
        output_dir=tmp_path.as_posix(),
    )

    assert response.recommended == ("staged[sobol,cmaes]",)
    assert response.fallbacks == ("random",)


def test_strategy_advisor_rejects_invalid_budget(tmp_path: Path) -> None:
    with pytest.raises(AgentWorkflowError, match="invalid-budget"):
        advise_optimization_strategy(
            StrategyAdvisorRequest(
                budget=0,
                has_categorical_parameters=True,
                scipy_available=False,
                cma_available=False,
            ),
            output_dir=tmp_path.as_posix(),
        )


def test_graphics_concierge_creates_manifested_sweep_artifacts(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg", force=True)

    sweep = SweepResult(
        evaluations=(
            EvalResult(
                theta={"alpha": 0.0, "beta": 0.0},
                objective=2.0,
                metrics={"m": 0.5},
                seed=1,
            ),
            EvalResult(
                theta={"alpha": 1.0, "beta": 1.0},
                objective=1.0,
                metrics={"m": 0.3},
                seed=2,
            ),
        ),
        seed=9,
        parameter_space=("alpha", "beta"),
        config_hash="h1",
        provenance={"suite": "test"},
    )
    result_path = tmp_path / "sweep.json"
    result_path.write_text(json.dumps(sweep.to_dict(), sort_keys=True), encoding="utf-8")

    response = run_graphics_concierge(
        GraphicsConciergeRequest(
            result_path=result_path.as_posix(),
            result_type="sweep",
            intents=(
                GraphicsIntent(kind="sweep_summary"),
                GraphicsIntent(kind="objective_slice_1d", x="alpha"),
            ),
            output_dir=(tmp_path / "artifacts").as_posix(),
            seed=9,
            config_hash="h1",
            provenance={"suite": "test"},
        )
    )

    manifest = response.manifest.to_dict()
    assert manifest["workflow"] == "graphics-concierge"
    assert len(manifest["artifacts"]) == 2
    for artifact in manifest["artifacts"]:
        assert Path(artifact["path"]).exists()


def test_graphics_concierge_rejects_unsupported_intent(tmp_path: Path) -> None:
    optimization = OptimizationHistory(
        evaluations=(EvalResult(theta={"x": 0.1}, objective=0.2, seed=1),),
        best=EvalResult(theta={"x": 0.1}, objective=0.2, seed=1),
        seed=1,
    )
    result_path = tmp_path / "opt.json"
    result_path.write_text(json.dumps(optimization.to_dict(), sort_keys=True), encoding="utf-8")

    with pytest.raises(AgentWorkflowError, match="unsupported-intent"):
        run_graphics_concierge(
            GraphicsConciergeRequest(
                result_path=result_path.as_posix(),
                result_type="optimization",
                intents=(
                    GraphicsIntent(kind="optimization_summary"),
                    GraphicsIntent(kind="metric_scatter", x="a", y="b"),
                ),
                output_dir=(tmp_path / "bad").as_posix(),
            )
        )
