# ADR 0005: Canonical run-summary artifact schema

- Status: Accepted
- Date: 2026-02-12

## Decision

Standardize deterministic run-summary JSON artifacts for both sweeps and optimizations:

- Add `build_sweep_summary` and `build_optimization_summary` helpers in harness reporting.
- Persist summaries with `save_summary` using sorted-key JSON.
- Lock common top-level fields: `run_type`, `seed`, `num_evaluations`, `parameter_space`, `config_hash`, `provenance`, and `objective` stats.
- Optimization summaries include `best` as canonical `EvalResult` serialization.

## Alternatives considered

1. Leave reporting to ad-hoc notebook scripts.
2. Emit separate incompatible summary formats per workflow.

Both alternatives were rejected because they increase downstream parsing drift and break reproducibility expectations.

## Consequences

- Downstream dashboards and agents can rely on one stable artifact shape.
- Report changes become explicit contract updates requiring tests and ADR updates.

## Validation

- Summary schema-lock tests in `tests/test_strategy_composition_and_reporting.py`.
