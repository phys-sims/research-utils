# How to write a harness adapter

Adapters convert simulator-specific evaluation calls into canonical `EvalResult` records.

## Adapter contract

Each adapter should expose:

- `run(config: dict[str, Any], seed: int) -> EvalResult`
- deterministic behavior for the same `(config, seed)` input
- no simulator-specific assumptions leaking into core harness contracts

## `PhysPipelineAdapter`

`PhysPipelineAdapter` in `research_utils.harness.adapters.phys_pipeline` is the reference optional adapter for `phys-pipeline`.

```python
from research_utils.harness.adapters.phys_pipeline import PhysPipelineAdapter

adapter = PhysPipelineAdapter(
    pipeline=my_pipeline_factory,
    objective_key="objective",
    metric_extractors={
        "rmse": lambda output: output["rmse"],
        "latency_ms": lambda output: output["timing_ms"],
    },
)
```

### Constructor inputs

- `pipeline`
  - a pipeline instance with `run(...)` or `evaluate(...)`, **or**
  - a factory callable that returns such an instance.
- `objective_key`
  - key extracted from pipeline output mapping as the canonical objective.
- `metric_extractors`
  - optional mapping from metric name to extractor callable.
  - each callable receives the raw pipeline output mapping.

### Optional dependency behavior

`phys-pipeline` is treated as optional. The adapter imports it only inside this module, and only when a default pipeline is requested (when `pipeline=None`). If unavailable, the adapter raises a clear `ImportError` describing what is missing.

### Canonical output

`run(...)` returns `EvalResult` with:

- `theta`: numeric values from `config`
- `objective`: float from `objective_key`
- `metrics`: extracted metric map
- `seed`: the explicit seed passed to `run`

Keep adapter logic thin and focused on translation only.
