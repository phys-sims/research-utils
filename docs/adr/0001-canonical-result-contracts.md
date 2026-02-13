# ADR 0001: Canonical result contracts for harness and optimization

- Status: Accepted
- Date: 2026-02-11

## Decision

Use `EvalResult`, `SweepResult`, and `OptimizationHistory` in `phys_sims_utils.shared.types`
as the canonical cross-layer contracts.

Key contract decisions:

- `EvalResult` is the single evaluation unit.
- `SweepResult` and `OptimizationHistory` are immutable collections of `EvalResult`.
- Results include determinism/provenance fields (`seed`, `config_hash`, `provenance`).
- Harness, plotting, and optimization all consume these same contracts.

## Alternatives considered

1. Separate type models per layer (harness-specific vs ml-specific).
2. Untyped dictionaries exchanged between modules.

Both were rejected because they increase drift risk and break contract-first API stability.

## Consequences

- Cross-layer tooling can share one serialization path.
- Integration tests can validate end-to-end behavior with one artifact schema.
- Breaking contract changes require ADR + version bump + roadmap update.

## Validation

- Contract tests in `tests/test_contract_types.py`.
- End-to-end artifact validation in `tests/test_end_to_end_dummy_example.py`.
