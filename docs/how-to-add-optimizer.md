# How to add an optimizer strategy

This guide documents the expected contract for optimizer strategies in
`research_utils.ml.strategies`.

## Strategy contract

Every strategy must implement the `OptimizerStrategy` protocol:

- `ask() -> Candidate`
- `tell(result: EvalResult) -> None`
- `is_converged` property
- `result` property (`OptimizationHistory`)

Strategies must keep deterministic behavior for identical seeds and parameter spaces.

## Optional dependencies

If a strategy requires third-party packages:

1. Guard imports in module scope and raise an actionable runtime error during strategy
   construction (`__post_init__`).
2. Mention the required install command in the error text.
3. Add dependency to `pyproject.toml` extras and documentation.
4. Add tests that skip gracefully if the optional dependency is unavailable.

## Example: `CMAESStrategy`

`CMAESStrategy` wraps the [`cma`](https://pypi.org/project/cma/) package.

```python
from research_utils.ml import Parameter, ParameterSpace
from research_utils.ml.strategies import CMAESStrategy

space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))
strategy = CMAESStrategy(parameter_space=space, seed=123)
```

### Behavior requirements implemented for CMA-ES

- Deterministic random seed (`seed` passed to the CMA backend).
- Bound-constrained candidate generation (`bounds` passed to CMA backend and output clipped).
- Runtime dependency guard with install guidance:
  - `pip install research-utils[ml]`
  - or `pip install cma`

## Testing checklist for new strategies

- Determinism test (`same seed => same ask() sequence`).
- Bound enforcement test for generated candidates.
- `tell()`/history update test, including best-so-far behavior.
- Optional dependency guard test.
- Use `pytest.importorskip("<dependency>")` for dependency-specific tests.
