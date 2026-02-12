# ADR 0003: Determinism policy and seed derivation

- Status: Accepted
- Date: 2026-02-12

## Decision

Adopt an explicit determinism policy for harness and optimization entrypoints:

- Public execution entrypoints require an explicit run seed unless explicitly configured otherwise.
- Child/evaluation seeds are derived deterministically from run seed + ordering index.
- Error paths in optimization are converted into deterministic penalty records.
- Provenance and config hashes are persisted in canonical result contracts.

## Alternatives considered

1. Allow implicit/global RNGs and optional seed propagation.
2. Require only top-level seeds without deterministic per-evaluation derivation.

Both alternatives were rejected because they make replay and regression debugging harder.

## Consequences

- Reproducibility is stable for sweeps/optimization under fixed inputs and seed.
- Implementations must avoid hidden randomness and preserve deterministic ordering.
- New public execution paths must follow the same seed + provenance requirements.

## Validation

- Determinism sweep tests in `tests/test_sweep_determinism.py`.
- Strategy and runner determinism tests in `tests/test_optimization_runner.py`.
- Penalty conversion determinism test in `tests/test_optimization_runner.py`.
