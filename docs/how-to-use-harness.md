# How to use the harness

This page shows one deterministic, end-to-end harness flow with a dummy simulator.

## End-to-end dummy simulation

Reference implementation: `examples/dummy_end_to_end.py`.

It exercises all v0.1 surfaces in one run:

- adapter translation (`PhysPipelineAdapter` + dummy pipeline)
- deterministic sweep execution (`InMemoryTestHarness` + `SweepSpec`)
- canonical plotting (`plot_objective_heatmap_2d`, `plot_metric_scatter`)
- optimization orchestration (`OptimizationRunner` + `RandomStrategy`)

```python
from pathlib import Path

from examples.dummy_end_to_end import run_example

artifacts = run_example(Path("artifacts/dummy_end_to_end"))
print(artifacts)
```

## Required deterministic inputs

- Always pass an explicit run seed.
- Keep sweep parameters and base config stable across reruns.
- Ensure adapter logic uses only `(config, seed)` for deterministic outputs.

## Output artifacts to validate

The example writes:

- `sweep_results.csv` (stable tabular result export)
- canonical sweep plots:
  - `objective_heatmap.png`
  - `metric_scatter.png`
- optimization plot:
  - `optimization_convergence.png`
- run metadata:
  - `run_metadata.json`
  - `dummy_optimization.metadata.json`

A matching integration test validates these artifacts in
`tests/test_end_to_end_dummy_example.py`.

## Private `*-testbench` integration checklist

Use this checklist before wiring your simulator:

- [ ] Install extras:
  - harness-only workflows: `pip install phys-sims-utils[harness]`
  - harness + optimization workflows: `pip install phys-sims-utils[harness,ml]`
- [ ] Make seed part of every public experiment entrypoint.
- [ ] Record provenance (repo commit, package versions, config hash).
- [ ] Emit canonical artifact layout:
  - results table (`*.csv` or `*.parquet`)
  - canonical plots (`*.png`)
  - run metadata (`*.metadata.json` or `run_metadata.json`)
- [ ] Confirm deterministic rerun behavior (`same inputs + same seed`).
