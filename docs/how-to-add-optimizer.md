# How to add an optimizer strategy

This guide documents the optimizer contract used by `OptimizationRunner`.

## Strategy contract (required)

Each strategy must implement the `OptimizerStrategy` protocol:

- `ask() -> Candidate`
- `tell(result: EvalResult) -> None`
- `is_converged` property
- `result` property (`OptimizationHistory`)

The strategy must be deterministic for the same parameter space and seed.

## Composition contract (v0.2)

Composition is also represented as an `OptimizerStrategy`:

- `StagedStrategy`: sequentially executes stage strategies and transitions when a stage converges or hits configured per-stage evaluation limits.
- `PortfolioStrategy`: deterministic round-robin dispatch across non-converged strategies.

Because composition stays inside the same protocol, existing `OptimizationRunner` integration does not change.

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

## Canonical summary artifacts (v0.2)

Use reporting helpers for stable machine-readable summaries:

```python
from research_utils.harness.reporting import build_optimization_summary, save_summary

summary = build_optimization_summary(history)
save_summary(summary, out / "optimization.summary.json")
```

Equivalent sweep summary helpers are available via `build_sweep_summary`.

## Artifact expectations for private `*-testbench` repos

When adding optimization in a private testbench, verify:

- [ ] extra selection is correct:
  - `research-utils[harness]` for sweep-only flows
  - `research-utils[harness,ml]` for optimization flows
- [ ] run seed is explicit and persisted in run metadata
- [ ] objective trace is written (`*.jsonl` + `*.csv` from `OptimizationLogger`)
- [ ] best-so-far snapshots are written (`*.best.jsonl`)
- [ ] convergence plot is generated (`optimization_convergence.png`)
- [ ] canonical summary is persisted (`optimization.summary.json`)
