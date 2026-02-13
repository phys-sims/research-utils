# ADR 0007: Mixed parameter-space contract for continuous + categorical workflows

- Status: Accepted
- Date: 2026-02-13

## Decision

Extend the public `Parameter`/`ParameterSpace` contracts to support mixed search spaces:

- `Parameter` can now be either bounded numeric (`bounds`) or categorical/discrete (`choices`).
- Encode/decode remains deterministic and stable:
  - numeric parameters encode to scalar floats,
  - categorical parameters encode to deterministic index positions in `choices`.
- `RandomStrategy` samples both parameter kinds deterministically from one explicit RNG seed.
- Numeric-only strategies (Sobol, CMA-ES) explicitly reject categorical parameters with clear errors.
- Reporting summaries include stable structure metadata (`structure_keys`, `structure_values`) to track topology decisions.

## Alternatives considered

1. Add categorical parameters in a separate contract type and keep `Parameter` numeric-only.
2. Keep summaries unchanged and require downstream parsers to infer structure fields from raw evaluations.

Both were rejected due to added contract fragmentation and reporting drift risk.

## Consequences

- v1.0 numeric workflows remain compatible.
- Mixed continuous + structural runs are now first-class and deterministic.
- Summary schema is expanded in a stable, explicit way for structure-aware analysis.

## Validation

- Parameter-space mixed encode/decode and categorical validation tests.
- Optimization determinism tests for mixed/topology candidates.
- Summary schema-lock tests for structure metadata fields.
- Agent tooling tests for `structure_fields` metadata generation and validation.
