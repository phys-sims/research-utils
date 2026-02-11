"""Core harness contracts."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Protocol

from research_utils.harness.metrics import MetricSpec
from research_utils.harness.sweep import SweepSpec, sample_points


@dataclass(frozen=True)
class EvalResult:
    """Canonical evaluation result shared across harness and ML."""

    objective: float
    metrics: dict[str, float] = field(default_factory=dict)
    parameters: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SweepResult:
    """Ordered collection of evaluations and sweep-level metadata."""

    evaluations: list[EvalResult]
    summary_metrics: dict[str, float]
    metadata: dict[str, Any]

    def to_dataframe(self) -> Any:
        """Return a pandas DataFrame when available, else row dictionaries."""
        rows = []
        for index, result in enumerate(self.evaluations):
            row: dict[str, Any] = {
                "index": index,
                "objective": result.objective,
                **{f"metric.{key}": value for key, value in result.metrics.items()},
                **{f"param.{key}": value for key, value in result.parameters.items()},
            }
            row.update({f"meta.{key}": value for key, value in result.metadata.items()})
            rows.append(row)

        try:
            import pandas as pd  # type: ignore[import-untyped]
        except ImportError:
            return rows
        return pd.DataFrame(rows)

    def save(self, path: str | Path) -> Path:
        """Persist sweep evaluations in CSV format."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        rows = self.to_dataframe()
        if hasattr(rows, "to_csv"):
            rows.to_csv(destination, index=False)
            return destination

        row_list = list(rows)
        if not row_list:
            destination.write_text("", encoding="utf-8")
            return destination

        fieldnames: list[str] = sorted({key for row in row_list for key in row})
        with destination.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(row_list)
        return destination


class SupportsRun(Protocol):
    def run(self, config: dict[str, Any], seed: int) -> EvalResult:
        """Run one deterministic evaluation."""


@dataclass
class TestHarness:
    __test__ = False

    """Minimal harness surface for adapter-backed evaluations."""

    name: str = "default"

    def evaluate(self, objective: float, metrics: dict[str, float] | None = None) -> EvalResult:
        """Build an ``EvalResult`` from deterministic caller-provided values."""
        return EvalResult(objective=objective, metrics=metrics or {})

    def run_sweep(
        self,
        adapter: SupportsRun,
        base_config: dict[str, Any],
        sweep_spec: SweepSpec,
        metric_spec: MetricSpec,
        seed: int | None,
    ) -> SweepResult:
        """Run a deterministic sweep and collect canonical evaluation records."""
        points = sample_points(sweep_spec, seed)
        run_seed = seed if seed is not None else 0

        evaluations: list[EvalResult] = []
        for index, point in enumerate(points):
            eval_seed = run_seed + index
            config = {**base_config, **point}
            raw_result = adapter.run(config=config, seed=eval_seed)

            metrics = metric_spec.compute(raw_result)
            metadata = {
                "eval_index": index,
                "eval_seed": eval_seed,
                "config_hash": _stable_hash(config),
                "harness": self.name,
            }
            metadata.update(raw_result.metadata)

            evaluations.append(
                EvalResult(
                    objective=raw_result.objective,
                    metrics=metrics,
                    parameters=point,
                    artifacts=raw_result.artifacts,
                    metadata=metadata,
                )
            )

        summary_metrics = metric_spec.aggregate(evaluations)
        sweep_metadata: dict[str, Any] = {
            "harness": self.name,
            "seed": seed,
            "mode": sweep_spec.mode,
            "parameter_names": sweep_spec.ordered_parameter_names(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        return SweepResult(evaluations=evaluations, summary_metrics=summary_metrics, metadata=sweep_metadata)


def _stable_hash(config: dict[str, Any]) -> str:
    normalized = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
