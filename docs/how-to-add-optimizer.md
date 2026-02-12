# How to add an optimizer strategy

This guide documents the optimizer contract used by `OptimizationRunner`.

## Strategy contract (required)

Each strategy must implement the `OptimizerStrategy` protocol:

- `ask() -> Candidate`
- `tell(result: EvalResult) -> None`
- `is_converged` property
- `result` property (`OptimizationHistory`)

The strategy must be deterministic for the same parameter space and seed.

## Dependency policy

If a strategy depends on third-party packages:

1. Keep the dependency optional (do not make it a core install dependency).
2. Raise an actionable runtime error if the dependency is unavailable.
3. Document the required extra in `pyproject.toml` and docs.
4. Add tests for both available and unavailable dependency paths.

## Runner integration pattern

The end-to-end reference in `examples/dummy_end_to_end.py` uses:

- `RandomStrategy` (always available baseline)
- `SimulationEvaluator` over an adapter
- `OptimizationRunner` for ask/tell orchestration
- `OptimizationLogger` for deterministic artifacts

```python
runner = OptimizationRunner(
    strategy=RandomStrategy(parameter_space=space, seed=21),
    evaluator=SimulationEvaluator(adapter=adapter),
    seed=21,
    logger=OptimizationLogger(output_dir=out, run_name="dummy_optimization"),
)
history = runner.run(iterations=8, batch_size=2)
```

## Artifact expectations for private `*-testbench` repos

When adding optimization in a private testbench, verify:

- [ ] extra selection is correct:
  - `research-utils[harness]` for sweep-only flows
  - `research-utils[harness,ml]` for optimization flows
- [ ] run seed is explicit and persisted in run metadata
- [ ] objective trace is written (`*.jsonl` + `*.csv` from `OptimizationLogger`)
- [ ] best-so-far snapshots are written (`*.best.jsonl`)
- [ ] convergence plot is generated (`optimization_convergence.png`)
