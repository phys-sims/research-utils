# phys-sims-utils

Shared research infrastructure for deterministic experimentation.

## Agent tooling quick answers

If you are evaluating the agent layer, start here: `docs/how-to-use-agents.md`.

It answers:

- how agents are used in this repo,
- whether MCP is required (it is optional), and
- what UX is available today for non-coding users.

## Optional dependency extras

Install only the surfaces you need:

- `pip install phys-sims-utils[harness]`
- `pip install phys-sims-utils[ml]`
- `pip install phys-sims-utils[agent]`
- `pip install phys-sims-utils[all]`

`phys-sims-utils[ml]` now includes optional optimizer dependencies used by built-in strategies:

- `scipy` for `SobolStrategy`
- `cma` for `CMAESStrategy`

If you only need CMA-ES support in an existing environment, install:

- `pip install cma`

## CMA-ES usage

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

`CMAESStrategy` is deterministic for the same parameter space and seed, enforces parameter
bounds for generated candidates, and raises an actionable `RuntimeError` at construction time if
`cma` is not installed.

`phys-pipeline` remains optional and adapter-scoped. Core modules in `phys_sims_utils.harness`,
`phys_sims_utils.ml`, and `phys_sims_utils.agents` must not require `phys-pipeline`; direct imports
are restricted to `phys_sims_utils.harness.adapters.phys_pipeline`.
