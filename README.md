# phys-sims-utils

`phys-sims-utils` is shared, simulation-agnostic infrastructure for **deterministic** research workflows:

- parameter sweeps and optimization orchestration,
- canonical result contracts (`EvalResult`, `SweepResult`, `OptimizationHistory`),
- reproducible reporting/plotting helpers, and
- agent tooling that generates artifacts without embedding physics logic.

This repository is designed to support simulation wrappers (for example, packages around `phys-pipeline`) and private testbench repos.

## Install

Install only the surfaces you need:

- `pip install phys-sims-utils[harness]`
- `pip install phys-sims-utils[ml]`
- `pip install phys-sims-utils[agent]`
- `pip install phys-sims-utils[all]`

`phys-sims-utils[ml]` includes optional optimizer dependencies used by built-in strategies:

- `scipy` for `SobolStrategy`
- `cma` for `CMAESStrategy`

If you only need CMA-ES support in an existing environment:

- `pip install cma`

## What you get

### Harness layer

- Deterministic sweep execution over a typed parameter space.
- Canonical metrics/objective collection through shared contracts.
- Stable persistence and plotting/reporting helpers for downstream analysis.

### ML/optimization layer

- Typed `Parameter` / `ParameterSpace` encode/decode APIs.
- Shared `OptimizerStrategy` ask/tell interface.
- Built-in deterministic strategies, including random, Sobol (optional), and CMA-ES (optional).
- Strategy composition support (staged and portfolio execution).

### Agent layer

- Deterministic experiment and workflow artifact generation.
- Repository validation tooling for reproducibility guardrails.
- Chat-oriented graphics/reporting concierge over canonical result contracts.

## Quick usage example (ML strategy)

```python
from phys_sims_utils.ml import Parameter, ParameterSpace
from phys_sims_utils.ml.strategies import CMAESStrategy

space = ParameterSpace(
    parameters=(
        Parameter("x", bounds=(-1.0, 1.0)),
        Parameter("y", bounds=(0.0, 5.0)),
    )
)

strategy = CMAESStrategy(parameter_space=space, seed=42)
candidate = strategy.ask()
# ... evaluate objective(candidate.theta) ...
```

`CMAESStrategy` is deterministic for the same parameter space and seed, enforces parameter bounds,
and raises a clear `RuntimeError` at construction time if `cma` is not installed.

## Docs map

- Current project status/roadmap: `STATUS.md`
- Harness usage: `docs/how-to-use-harness.md`
- Optimizer integration: `docs/how-to-add-optimizer.md`
- Adapter integration: `docs/how-to-write-adapter.md`
- Agent tooling quickstart: `docs/how-to-use-agents.md`
- Architecture decisions: `docs/adr/`

## Dependency boundary note

`phys-pipeline` remains optional and adapter-scoped. Core modules in
`phys_sims_utils.harness`, `phys_sims_utils.ml`, and `phys_sims_utils.agents`
must not require `phys-pipeline`; direct imports are restricted to
`phys_sims_utils.harness.adapters.phys_pipeline`.
