# ADR 0002: Optional dependency boundaries and extras

- Status: Accepted
- Date: 2026-02-11

## Decision

Keep heavy/optional dependencies behind extras and module boundaries:

- plotting deps in `[harness]`
- optimization deps in `[ml]`
- adapter-specific external simulator deps scoped to adapter modules

Package extras are defined in `pyproject.toml` and should map to workflow surfaces:

- `phys-sims-utils[harness]`
- `phys-sims-utils[harness,ml]`

## Alternatives considered

1. Install all dependencies by default.
2. Hide import failures silently and degrade behavior.

Both were rejected to avoid unnecessary installs and hidden nondeterministic behavior.

## Consequences

- Testbench repos can install only required surfaces.
- Missing optional dependencies fail with explicit runtime guidance.
- Core packages remain simulation-agnostic and lightweight.

## Validation

- Optional dependency behavior covered by plotting/strategy tests.
- End-to-end dummy example validates expected artifacts with `harness+ml` dependencies.
