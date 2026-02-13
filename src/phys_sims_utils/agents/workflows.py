"""Agent-first workflow contracts and deterministic helpers for v1.2."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from phys_sims_utils.agents.repo_checks import RepoIssue, check_script_metadata
from phys_sims_utils.harness import (
    build_optimization_summary,
    build_sweep_summary,
    save_summary,
)
from phys_sims_utils.harness.plotting import (
    plot_convergence_best_so_far,
    plot_metric_scatter,
    plot_objective_heatmap_2d,
    plot_objective_slice_1d,
)
from phys_sims_utils.shared import OptimizationHistory, SweepResult


@dataclass(frozen=True)
class AgentWorkflowError(Exception):
    """Structured workflow error for invalid requests."""

    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


@dataclass(frozen=True)
class AgentArtifactRecord:
    """Single generated artifact metadata record."""

    name: str
    path: str
    artifact_type: str


@dataclass(frozen=True)
class AgentArtifactManifest:
    """Stable manifest schema for agent workflow outputs."""

    workflow: str
    seed: int
    config_hash: str
    provenance: dict[str, str]
    artifacts: tuple[AgentArtifactRecord, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow": self.workflow,
            "seed": self.seed,
            "config_hash": self.config_hash,
            "provenance": dict(self.provenance),
            "artifacts": [
                {"name": item.name, "path": item.path, "artifact_type": item.artifact_type}
                for item in self.artifacts
            ],
        }


@dataclass(frozen=True)
class AdaptationAssistantRequest:
    """Request envelope for repository adaptation assistance."""

    project_root: str
    output_dir: str
    valid_parameter_paths: tuple[str, ...]
    seed: int = 0
    config_hash: str = ""
    provenance: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AdaptationAssistantResponse:
    """Structured deterministic adaptation output."""

    manifest: AgentArtifactManifest
    findings: tuple[RepoIssue, ...]
    checklist: tuple[str, ...]


@dataclass(frozen=True)
class StrategyAdvisorRequest:
    """Request envelope for deterministic strategy advisory."""

    budget: int
    has_categorical_parameters: bool
    scipy_available: bool
    cma_available: bool
    allow_composition: bool = True
    seed: int = 0
    config_hash: str = ""
    provenance: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class StrategyAdvisorResponse:
    """Structured deterministic recommendation output."""

    manifest: AgentArtifactManifest
    recommended: tuple[str, ...]
    rationale: tuple[str, ...]
    fallbacks: tuple[str, ...]


@dataclass(frozen=True)
class GraphicsIntent:
    """Single visualization/summary intent."""

    kind: Literal[
        "sweep_summary",
        "optimization_summary",
        "objective_slice_1d",
        "objective_heatmap_2d",
        "metric_scatter",
        "convergence_plot",
    ]
    x: str | None = None
    y: str | None = None


@dataclass(frozen=True)
class GraphicsConciergeRequest:
    """Request envelope for chat-oriented graphics/reporting concierge."""

    result_path: str
    result_type: Literal["sweep", "optimization"]
    intents: tuple[GraphicsIntent, ...]
    output_dir: str
    seed: int = 0
    config_hash: str = ""
    provenance: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphicsConciergeResponse:
    """Structured output for generated plot/report artifacts."""

    manifest: AgentArtifactManifest


def run_adaptation_assistant(request: AdaptationAssistantRequest) -> AdaptationAssistantResponse:
    """Inspect repository scripts and emit deterministic adaptation artifacts."""
    root = Path(request.project_root)
    output_dir = Path(request.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    findings: list[RepoIssue] = []
    for script_path in sorted(root.rglob("*.py")):
        result = check_script_metadata(
            script_path,
            valid_parameter_paths=set(request.valid_parameter_paths),
        )
        findings.extend(result.issues)

    findings = sorted(findings, key=lambda issue: (issue.code, issue.message))
    checklist = _adaptation_checklist(findings)

    report_payload = {
        "findings": [
            {"code": issue.code, "message": issue.message}
            for issue in findings
        ],
        "checklist": list(checklist),
    }
    report_path = output_dir / "adaptation_report.json"
    report_path.write_text(json.dumps(report_payload, sort_keys=True, indent=2), encoding="utf-8")

    manifest = AgentArtifactManifest(
        workflow="adaptation-assistant",
        seed=request.seed,
        config_hash=request.config_hash,
        provenance=dict(request.provenance),
        artifacts=(
            AgentArtifactRecord(
                name="adaptation-report",
                path=report_path.as_posix(),
                artifact_type="json",
            ),
        ),
    )
    _write_manifest(output_dir / "manifest.json", manifest)

    return AdaptationAssistantResponse(
        manifest=manifest,
        findings=tuple(findings),
        checklist=checklist,
    )


def advise_optimization_strategy(
    request: StrategyAdvisorRequest,
    *,
    output_dir: str,
) -> StrategyAdvisorResponse:
    """Emit deterministic optimization strategy recommendations."""
    if request.budget <= 0:
        raise AgentWorkflowError(
            code="invalid-budget",
            message="budget must be positive",
        )

    recommendation: list[str] = []
    rationale: list[str] = []
    fallbacks: list[str] = ["random"]

    if request.has_categorical_parameters:
        recommendation.append("random")
        rationale.append("Categorical parameters require strategies supporting mixed spaces.")
    else:
        if (
            request.budget >= 40
            and request.scipy_available
            and request.cma_available
            and request.allow_composition
        ):
            recommendation.append("staged[sobol,cmaes]")
            rationale.append("Large numeric budget benefits from global then local search.")
        elif request.scipy_available and request.budget >= 16:
            recommendation.append("sobol")
            rationale.append("Sobol covers numeric spaces efficiently under moderate budget.")
        else:
            recommendation.append("random")
            rationale.append(
                "Random strategy is always available and deterministic with explicit seed."
            )

    if not request.scipy_available:
        fallbacks.append("sobol-unavailable-no-scipy")
    if not request.cma_available:
        fallbacks.append("cmaes-unavailable-no-cma")

    output_root = Path(output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    rec_path = output_root / "strategy_advice.json"
    rec_payload = {
        "recommended": recommendation,
        "rationale": rationale,
        "fallbacks": fallbacks,
    }
    rec_path.write_text(json.dumps(rec_payload, sort_keys=True, indent=2), encoding="utf-8")

    manifest = AgentArtifactManifest(
        workflow="strategy-advisor",
        seed=request.seed,
        config_hash=request.config_hash,
        provenance=dict(request.provenance),
        artifacts=(
            AgentArtifactRecord(
                name="strategy-advice",
                path=rec_path.as_posix(),
                artifact_type="json",
            ),
        ),
    )
    _write_manifest(output_root / "manifest.json", manifest)

    return StrategyAdvisorResponse(
        manifest=manifest,
        recommended=tuple(recommendation),
        rationale=tuple(rationale),
        fallbacks=tuple(fallbacks),
    )


def run_graphics_concierge(request: GraphicsConciergeRequest) -> GraphicsConciergeResponse:
    """Generate canonical summaries/plots from canonical result artifacts."""
    output_dir = Path(request.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(Path(request.result_path).read_text(encoding="utf-8"))

    artifacts: list[AgentArtifactRecord] = []
    if request.result_type == "sweep":
        sweep_result = SweepResult.from_dict(payload)
        artifacts.extend(_run_sweep_intents(sweep_result, request.intents, output_dir))
    elif request.result_type == "optimization":
        optimization_result = OptimizationHistory.from_dict(payload)
        artifacts.extend(
            _run_optimization_intents(optimization_result, request.intents, output_dir)
        )
    else:
        raise AgentWorkflowError("unsupported-result-type", request.result_type)

    manifest = AgentArtifactManifest(
        workflow="graphics-concierge",
        seed=request.seed,
        config_hash=request.config_hash,
        provenance=dict(request.provenance),
        artifacts=tuple(artifacts),
    )
    _write_manifest(output_dir / "manifest.json", manifest)
    return GraphicsConciergeResponse(manifest=manifest)


def _run_sweep_intents(
    result: SweepResult,
    intents: tuple[GraphicsIntent, ...],
    output_dir: Path,
) -> list[AgentArtifactRecord]:
    artifacts: list[AgentArtifactRecord] = []
    for intent in intents:
        if intent.kind == "sweep_summary":
            path = save_summary(build_sweep_summary(result), output_dir / "sweep.summary.json")
            artifacts.append(AgentArtifactRecord("sweep-summary", path.as_posix(), "json"))
        elif intent.kind == "objective_slice_1d":
            if intent.x is None:
                raise AgentWorkflowError("missing-x-parameter", "objective_slice_1d requires x")
            path = plot_objective_slice_1d(
                result,
                parameter=intent.x,
                output_path=output_dir / f"objective_slice_{intent.x}.png",
            )
            artifacts.append(AgentArtifactRecord("objective-slice-1d", path.as_posix(), "png"))
        elif intent.kind == "objective_heatmap_2d":
            if intent.x is None or intent.y is None:
                raise AgentWorkflowError(
                    "missing-heatmap-axes",
                    "objective_heatmap_2d requires x and y",
                )
            path = plot_objective_heatmap_2d(
                result,
                x_parameter=intent.x,
                y_parameter=intent.y,
                output_path=output_dir / f"objective_heatmap_{intent.x}_{intent.y}.png",
            )
            artifacts.append(AgentArtifactRecord("objective-heatmap-2d", path.as_posix(), "png"))
        elif intent.kind == "metric_scatter":
            if intent.x is None or intent.y is None:
                raise AgentWorkflowError("missing-metrics", "metric_scatter requires x and y")
            path = plot_metric_scatter(
                result,
                x_metric=intent.x,
                y_metric=intent.y,
                output_path=output_dir / f"metric_scatter_{intent.x}_{intent.y}.png",
            )
            artifacts.append(AgentArtifactRecord("metric-scatter", path.as_posix(), "png"))
        else:
            raise AgentWorkflowError("unsupported-intent", intent.kind)
    return artifacts


def _run_optimization_intents(
    result: OptimizationHistory,
    intents: tuple[GraphicsIntent, ...],
    output_dir: Path,
) -> list[AgentArtifactRecord]:
    artifacts: list[AgentArtifactRecord] = []
    for intent in intents:
        if intent.kind == "optimization_summary":
            path = save_summary(
                build_optimization_summary(result),
                output_dir / "optimization.summary.json",
            )
            artifacts.append(AgentArtifactRecord("optimization-summary", path.as_posix(), "json"))
        elif intent.kind == "convergence_plot":
            path = plot_convergence_best_so_far(result, output_path=output_dir / "convergence.png")
            artifacts.append(AgentArtifactRecord("convergence-plot", path.as_posix(), "png"))
        else:
            raise AgentWorkflowError("unsupported-intent", intent.kind)
    return artifacts


def _adaptation_checklist(findings: list[RepoIssue]) -> tuple[str, ...]:
    by_code = {issue.code for issue in findings}
    checklist: list[str] = []
    if "missing-seed-policy" in by_code or "missing-seed-argument" in by_code:
        checklist.append(
            "Add explicit seed policy metadata and a required main(seed=...) "
            "entrypoint."
        )
    if "missing-config-hash" in by_code or "missing-provenance" in by_code:
        checklist.append("Add config hash and provenance metadata headers to generated scripts.")
    if "invalid-parameter-path" in by_code:
        checklist.append("Align PARAMETER_PATHS with canonical ParameterSpace paths.")
    if "missing-structure-metadata" in by_code:
        checklist.append("Include structure_fields metadata for topology-aware workflows.")
    if not checklist:
        checklist.append("No blocking adaptation issues detected.")
    return tuple(checklist)


def _write_manifest(path: Path, manifest: AgentArtifactManifest) -> None:
    path.write_text(json.dumps(manifest.to_dict(), sort_keys=True, indent=2), encoding="utf-8")


__all__ = [
    "AdaptationAssistantRequest",
    "AdaptationAssistantResponse",
    "AgentArtifactManifest",
    "AgentArtifactRecord",
    "AgentWorkflowError",
    "GraphicsConciergeRequest",
    "GraphicsConciergeResponse",
    "GraphicsIntent",
    "StrategyAdvisorRequest",
    "StrategyAdvisorResponse",
    "advise_optimization_strategy",
    "run_adaptation_assistant",
    "run_graphics_concierge",
]
