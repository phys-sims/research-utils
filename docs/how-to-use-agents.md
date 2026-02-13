# How to use the agent tooling

This page explains what is (and is not) "agentic" in `phys-sims-utils`.

## TL;DR

- You **do not** need to write an MCP server to use the built-in agent tooling.
- UX is still **library-first** (Python APIs and deterministic artifacts).
- v1.2 adds structured workflow contracts for adaptation, strategy advice, and graphics intents.

## What the agent layer provides

The agent layer in `phys_sims_utils.agents` focuses on deterministic infrastructure tasks:

- **Experiment generation**: `generate_experiment_script(...)` writes reproducible scripts with
  seed policy, config hash, and provenance headers.
- **Repository/policy checks**: `check_script_metadata(...)` validates reproducibility requirements.
- **Project introspection**: `build_introspection_report(...)` emits stable doc/test hints.
- **Repository adaptation assistant**: `run_adaptation_assistant(...)` emits deterministic findings,
  checklist guidance, and a manifest artifact.
- **Optimization strategy advisor**: `advise_optimization_strategy(...)` emits deterministic strategy
  recommendations with rationale and fallback paths.
- **Graphics concierge**: `run_graphics_concierge(...)` maps structured intents to canonical
  plotting/reporting artifacts over `SweepResult` and `OptimizationHistory` inputs.

All workflows are simulation-agnostic and artifact-oriented.

## Do I need MCP?

No, not for this repo's agent tooling.

Use cases:

1. Direct Python usage in scripts/notebooks.
2. CI usage where workflow artifacts are quality gates.
3. Wrapper usage where a chat/orchestration layer calls these Python contracts.

## Minimal v1.2 usage example

```python
import json
from pathlib import Path

from phys_sims_utils.agents import (
    GraphicsConciergeRequest,
    GraphicsIntent,
    StrategyAdvisorRequest,
    advise_optimization_strategy,
    run_graphics_concierge,
)

advice = advise_optimization_strategy(
    StrategyAdvisorRequest(
        budget=40,
        has_categorical_parameters=False,
        scipy_available=True,
        cma_available=False,
        seed=7,
        config_hash="cfg-123",
    ),
    output_dir="artifacts/advice",
)

request = GraphicsConciergeRequest(
    result_path="artifacts/sweep_result.json",
    result_type="sweep",
    intents=(
        GraphicsIntent(kind="sweep_summary"),
        GraphicsIntent(kind="objective_slice_1d", x="alpha"),
    ),
    output_dir="artifacts/graphics",
    seed=7,
    config_hash="cfg-123",
)
response = run_graphics_concierge(request)

print(json.dumps(advice.manifest.to_dict(), indent=2, sort_keys=True))
print(json.dumps(response.manifest.to_dict(), indent=2, sort_keys=True))
```
