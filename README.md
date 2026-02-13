# research-utils

Shared research infrastructure for deterministic experimentation.

## Agent tooling quick answers

If you are evaluating the agent layer, start here: `docs/how-to-use-agents.md`.

It answers:

- how agents are used in this repo,
- whether MCP is required (it is optional), and
- what UX is available today for non-coding users.

## Optional dependency extras

Install only the surfaces you need:

- `pip install research-utils[harness]`
- `pip install research-utils[ml]`
- `pip install research-utils[agent]`
- `pip install research-utils[all]`

`research-utils[ml]` now includes optional optimizer dependencies used by built-in strategies:

- `scipy` for `SobolStrategy`
- `cma` for `CMAESStrategy`

If you only need CMA-ES support in an existing environment, install:

- `pip install cma`

## CMA-ES usage

```python
from research_utils.ml import Parameter, ParameterSpace
from research_utils.ml.strategies import CMAESStrategy

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

`phys-pipeline` remains optional and adapter-scoped. Core modules in `research_utils.harness`,
`research_utils.ml`, and `research_utils.agents` must not require `phys-pipeline`; direct imports
are restricted to `research_utils.harness.adapters.phys_pipeline`.
