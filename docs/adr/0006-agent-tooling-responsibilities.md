# ADR 0006: Agent tooling responsibilities and limits

- Status: Accepted
- Date: 2026-02-12

## Decision

Define explicit scope boundaries for `sim_utils.agents`:

- Agent utilities may generate deterministic artifacts (scripts, reports, validation outputs).
- Agent utilities must remain simulation-agnostic and must not embed physics/domain truth.
- Agent utilities must avoid hidden side effects (no implicit execution of experiments, no mutation outside explicit output paths).
- Reproducibility checks are mandatory for generated experiment scripts:
  - seed policy marker
  - seed argument presence
  - config hash marker
  - provenance marker
  - parameter path validity

## Alternatives considered

1. Permit agent utilities to run simulations directly.
2. Couple agent checks to simulator-specific assumptions.
3. Treat agent outputs as best-effort text without deterministic guarantees.

These were rejected because they violate repository boundaries and contract-first reproducibility goals.

## Consequences

- Agent workflows can be safely reused across multiple simulation libraries/testbenches.
- Generated artifacts are auditable and deterministic under fixed inputs.
- Guardrail checks provide immediate, structured feedback when reproducibility metadata is missing.

## Validation

- Golden-file generation stability in `tests/test_agents_tools.py`.
- Metadata/reproducibility guardrail checks in `tests/test_agents_tools.py`.
- Deterministic introspection output checks in `tests/test_agents_tools.py`.
