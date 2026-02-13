# How to write a harness adapter

Adapters convert simulator-specific calls into canonical `EvalResult` records.

## Adapter contract

Each adapter must expose:

- `run(config: dict[str, Any], seed: int) -> EvalResult`
- deterministic behavior for identical `(config, seed)` inputs
- explicit, stable objective/metric extraction

Keep adapters thin. Put simulator-specific assumptions only in adapter modules.

## Reference: `PhysPipelineAdapter`

`phys_sims_utils.harness.adapters.phys_pipeline.PhysPipelineAdapter` is the template.

```python
adapter = PhysPipelineAdapter(
    pipeline=my_pipeline_factory_or_instance,
    objective_key="objective",
    metric_extractors={"rmse": lambda out: out["rmse"]},
)
```

### Constructor inputs

- `pipeline`: instance or factory exposing `run(...)` or `evaluate(...)`
- `objective_key`: key used for canonical objective
- `metric_extractors`: optional mapping of metric name to extractor callable

### Optional dependency behavior

`phys-pipeline` remains optional and adapter-scoped. Core harness/ML modules do not
import it directly.

## End-to-end dummy example

Use `examples/dummy_end_to_end.py` to validate adapter behavior inside a complete flow:

- adapter run output mapped to `EvalResult`
- deterministic sweep via `InMemoryTestHarness`
- plotting and optimization artifacts generated from canonical types

## Private `*-testbench` adapter checklist

- [ ] Adapter accepts explicit `seed` and forwards it deterministically.
- [ ] Adapter returns canonical `EvalResult` fields (`theta`, `objective`, `metrics`).
- [ ] Adapter includes enough provenance/config metadata for reruns.
- [ ] Adapter does not leak domain logic into harness/ML core packages.
