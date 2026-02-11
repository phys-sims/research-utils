"""Optional adapter boundary for phys-pipeline integration."""

from __future__ import annotations

# Optional and intentionally isolated to adapters.
import phys_pipeline  # type: ignore[import-not-found]

from research_utils.harness import EvalResult


class PhysPipelineAdapter:
    """Thin adapter wrapper for optional ``phys_pipeline`` integration."""

    def run(self) -> EvalResult:
        _ = phys_pipeline
        return EvalResult(objective=0.0)
