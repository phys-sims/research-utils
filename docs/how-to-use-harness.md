# How to use the harness

`InMemoryTestHarness` runs deterministic sweeps by combining:

- a `SweepSpec` for parameter sampling
- an adapter that returns `EvalResult`
- optional metric specs for aggregation

## Example: running a sweep with `PhysPipelineAdapter`

```python
from research_utils.harness import InMemoryTestHarness, SweepSpec
from research_utils.harness.adapters.phys_pipeline import PhysPipelineAdapter

harness = InMemoryTestHarness(name="research")

adapter = PhysPipelineAdapter(
    pipeline=my_pipeline_factory,
    objective_key="objective",
    metric_extractors={"rmse": lambda output: output["rmse"]},
)

sweep = SweepSpec(parameters={"alpha": (0.1, 0.2, 0.3)}, mode="grid")
result = harness.run_sweep(
    adapter=adapter,
    base_config={"dataset": "experiment_a"},
    sweep_spec=sweep,
    seed=123,
)
```

## Determinism rules

- always pass an explicit seed to `run_sweep`
- adapter `run(...)` should use the supplied seed without hidden RNGs
- repeated runs with the same seed should produce identical sweep ordering and outputs

## Reading results

`SweepResult` exposes:

- `evaluations`: tuple of `EvalResult`
- `seed`: run-level seed
- `parameter_space`: canonical parameter ordering
- `config_hash` and `provenance`: reproducibility metadata

Persist results with `SweepResult.save(...)` when needed.
