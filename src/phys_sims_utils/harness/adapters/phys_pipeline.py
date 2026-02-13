"""Optional adapter for integrating ``phys-pipeline`` with the harness."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from importlib import import_module
from typing import Any, Protocol, cast

from phys_sims_utils.shared import EvalResult


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

        pipeline = _call_with_optional_seed(cast(PipelineFactory, candidate), seed)
        if not _is_pipeline_instance(pipeline):
            msg = (
                "Pipeline factory must return an instance exposing 'run' or 'evaluate'."
            )
            raise TypeError(msg)
        return cast(_PipelineProtocol, pipeline)

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
            output = _call_with_config_and_seed(method, config=config, seed=seed)
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

    pipeline = _call_with_optional_seed(cast(PipelineFactory, factory), seed)
    if not _is_pipeline_instance(pipeline):
        msg = "phys-pipeline 'Pipeline' entrypoint returned an invalid pipeline object."
        raise TypeError(msg)
    return cast(_PipelineProtocol, pipeline)


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


def _call_with_optional_seed(function: Callable[..., Any], seed: int) -> Any:
    if _supports_kwargs(function, ("seed",)):
        return function(seed=seed)
    if _supports_positional(function, 1):
        return function(seed)
    return function()


def _call_with_config_and_seed(
    function: Callable[..., Any], *, config: Mapping[str, Any], seed: int
) -> Any:
    if _supports_kwargs(function, ("config", "seed")):
        return function(config=config, seed=seed)
    if _supports_positional(function, 2):
        return function(config, seed)
    msg = "Pipeline method must accept config and seed parameters."
    raise TypeError(msg)


def _supports_kwargs(function: Callable[..., Any], keys: tuple[str, ...]) -> bool:
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        return False

    parameters = signature.parameters
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in parameters.values()):
        return True

    return all(
        key in parameters
        and parameters[key].kind
        in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
        for key in keys
    )


def _supports_positional(function: Callable[..., Any], expected_count: int) -> bool:
    try:
        signature = inspect.signature(function)
    except (TypeError, ValueError):
        return True

    params = list(signature.parameters.values())
    required_positional = [
        param
        for param in params
        if param.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        and param.default is inspect.Parameter.empty
    ]
    if len(required_positional) > expected_count:
        return False

    positional_capacity = sum(
        1
        for param in params
        if param.kind
        in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    if any(param.kind == inspect.Parameter.VAR_POSITIONAL for param in params):
        return True

    return positional_capacity >= expected_count


__all__ = ["MetricExtractor", "PhysPipelineAdapter"]
