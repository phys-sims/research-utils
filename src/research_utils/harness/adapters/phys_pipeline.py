"""Optional adapter boundary for phys-pipeline integration."""

from __future__ import annotations

from typing import Any

# Optional and intentionally isolated to adapters.
import phys_pipeline  # type: ignore[import-not-found]

from research_utils.shared import EvalResult


class PhysPipelineAdapter:
    """Thin adapter wrapper for optional ``phys_pipeline`` integration."""

    def run(self, config: dict[str, Any], seed: int) -> EvalResult:
        _ = phys_pipeline
        return EvalResult(
            theta={
                k: float(v) for k, v in config.items() if isinstance(v, (int, float))
            },
            objective=0.0,
            seed=seed,
        )
