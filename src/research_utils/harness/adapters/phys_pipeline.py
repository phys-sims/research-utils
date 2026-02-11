"""Optional adapter for integrating ``phys-pipeline`` with the harness."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from importlib import import_module
from typing import Any, Protocol, cast

from research_utils.shared import EvalResult


class _PipelineProtocol(Protocol):
    def run(self, config: Mapping[str, Any], seed: int) -> Mapping[str, Any]:
        """Execute one simulation evaluation."""


MetricExtractor = Callable[[Mapping[str, Any]], float]
PipelineFactory = Callable[..., _PipelineProtocol]


class PhysPipelineAdapter:
    """Thin adapter that converts pipeline outputs into canonical ``EvalResult`` records."""

    def __init__(
        self,
        pipeline: _PipelineProtocol | PipelineFactory | None = None,
        *,
        objective_key: str,
        metric_extractors: Mapping[str, MetricExtractor] | None = None,
    ) -> None:
        self._pipeline_or_factory = pipeline
        self._objective_key = objective_key
        self._metric_extractors = dict(metric_extractors or {})

    def run(self, config: dict[str, Any], seed: int) -> EvalResult:
        pipeline = self._resolve_pipeline(seed=seed)
        raw_output = self._run_pipeline(pipeline=pipeline, config=config, seed=seed)

        if self._objective_key not in raw_output:
            msg = (
                f"Pipeline output is missing objective key '{self._objective_key}'. "
                f"Available keys: {sorted(raw_output.keys())}"
            )
            raise KeyError(msg)

        metrics = {
            metric_name: float(extractor(raw_output))
            for metric_name, extractor in self._metric_extractors.items()
        }

        return EvalResult(
            theta=_numeric_theta(config),
            objective=float(raw_output[self._objective_key]),
            metrics=metrics,
            seed=seed,
        )

    def _resolve_pipeline(self, seed: int) -> _PipelineProtocol:
        if self._pipeline_or_factory is None:
            return _default_pipeline(seed=seed)

        candidate = self._pipeline_or_factory
        if _is_pipeline_instance(candidate):
            return cast(_PipelineProtocol, candidate)

        factory = cast(PipelineFactory, candidate)
        try:
            return factory(seed=seed)
        except TypeError:
            try:
                return factory(seed)
            except TypeError:
                return factory()

    def _run_pipeline(
        self,
        *,
        pipeline: _PipelineProtocol,
        config: Mapping[str, Any],
        seed: int,
    ) -> Mapping[str, Any]:
        for method_name in ("run", "evaluate"):
            method = getattr(pipeline, method_name, None)
            if method is None:
                continue
            try:
                output = method(config=config, seed=seed)
            except TypeError:
                output = method(config, seed)

            if not isinstance(output, Mapping):
                msg = (
                    "Pipeline methods must return a mapping of objective/metrics, "
                    f"got {type(output).__name__}."
                )
                raise TypeError(msg)
            return output

        msg = "Pipeline object must expose a 'run' or 'evaluate' method."
        raise TypeError(msg)


def _is_pipeline_instance(value: object) -> bool:
    return hasattr(value, "run") or hasattr(value, "evaluate")


def _default_pipeline(*, seed: int) -> _PipelineProtocol:
    module = _import_phys_pipeline()

    factory = getattr(module, "Pipeline", None)
    if factory is None:
        msg = "phys-pipeline module is missing required 'Pipeline' entrypoint."
        raise RuntimeError(msg)

    try:
        return cast(_PipelineProtocol, factory(seed=seed))
    except TypeError:
        try:
            return cast(_PipelineProtocol, factory(seed))
        except TypeError:
            return cast(_PipelineProtocol, factory())


def _import_phys_pipeline() -> Any:
    try:
        return import_module("phys_pipeline")
    except ImportError as exc:  # pragma: no cover - depends on optional package
        msg = (
            "PhysPipelineAdapter requires optional dependency 'phys-pipeline' when no "
            "pipeline instance/factory is provided. Install it with the simulation package "
            "that provides phys_pipeline."
        )
        raise ImportError(msg) from exc


def _numeric_theta(config: Mapping[str, Any]) -> dict[str, float]:
    return {
        key: float(value)
        for key, value in config.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }


__all__ = ["MetricExtractor", "PhysPipelineAdapter"]
