"""Deterministic optimization logging utilities."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sim_utils.shared import EvalResult


@dataclass
class OptimizationLogger:
    """Write per-evaluation optimization logs as JSONL and CSV."""

    output_dir: Path
    run_name: str = "optimization"
    run_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.jsonl_path = self.output_dir / f"{self.run_name}.jsonl"
        self.csv_path = self.output_dir / f"{self.run_name}.csv"
        self.best_path = self.output_dir / f"{self.run_name}.best.jsonl"
        self.metadata_path = self.output_dir / f"{self.run_name}.metadata.json"

        self.metadata_path.write_text(
            json.dumps(self.run_metadata, sort_keys=True, indent=2),
            encoding="utf-8",
        )

        self._jsonl = self.jsonl_path.open("w", encoding="utf-8")
        self._best_jsonl = self.best_path.open("w", encoding="utf-8")
        self._csv = self.csv_path.open("w", encoding="utf-8", newline="")

        fieldnames = [
            "iteration",
            "objective",
            "best_objective",
            "seed",
            "theta",
            "metrics",
            "artifacts",
            "timestamp",
            "config_hash",
            "provenance",
        ]
        self._writer = csv.DictWriter(self._csv, fieldnames=fieldnames)
        self._writer.writeheader()
        self._best_objective: float | None = None

    def log_evaluation(self, iteration: int, result: EvalResult, best: EvalResult | None) -> None:
        """Append one evaluation row and a best-so-far snapshot when improved."""
        best_objective = best.objective if best is not None else result.objective
        payload = {
            "iteration": iteration,
            "objective": result.objective,
            "best_objective": best_objective,
            "seed": result.seed,
            "theta": dict(result.theta),
            "metrics": dict(result.metrics),
            "artifacts": dict(result.artifacts),
            "timestamp": result.timestamp.isoformat(),
            "config_hash": result.config_hash,
            "provenance": dict(result.provenance),
        }

        self._jsonl.write(json.dumps(payload, sort_keys=True) + "\n")
        self._jsonl.flush()

        csv_row = {
            **payload,
            "theta": json.dumps(payload["theta"], sort_keys=True),
            "metrics": json.dumps(payload["metrics"], sort_keys=True),
            "artifacts": json.dumps(payload["artifacts"], sort_keys=True),
            "provenance": json.dumps(payload["provenance"], sort_keys=True),
        }
        self._writer.writerow(csv_row)
        self._csv.flush()

        is_new_best = self._best_objective is None or result.objective <= self._best_objective
        if is_new_best:
            self._best_objective = result.objective
            self._best_jsonl.write(json.dumps(payload, sort_keys=True) + "\n")
            self._best_jsonl.flush()

    def close(self) -> None:
        self._jsonl.close()
        self._best_jsonl.close()
        self._csv.close()


__all__ = ["OptimizationLogger"]
