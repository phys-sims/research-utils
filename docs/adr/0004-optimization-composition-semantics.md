# ADR 0004: Optimization composition semantics (staged and portfolio)

- Status: Accepted
- Date: 2026-02-12

## Decision

Define v1 composition semantics behind the existing `OptimizerStrategy` ask/tell contract:

- `StagedStrategy` executes strategies in sequence.
  - Stage transitions occur when the current stage converges, or when an explicit per-stage iteration cap is reached.
- `PortfolioStrategy` dispatches ask/tell in deterministic round-robin across non-converged strategies.
- Both strategies expose a single merged result history and best-so-far behavior through `OptimizationHistory`.

## Alternatives considered

1. Introduce a new composition-specific runner API separate from `OptimizerStrategy`.
2. Use randomized portfolio allocation.

Both alternatives were rejected to keep composition simulation-agnostic and deterministic under the same contracts.

## Consequences

- Existing `OptimizationRunner` can execute composed strategies with no API changes.
- Composition behavior is testable via deterministic integration tests.
- Additional composition policies (weighted/UCB/etc.) can be added later without contract changes.

## Validation

- Stage transition tests in `tests/test_strategy_composition_and_reporting.py`.
- Round-robin portfolio allocation tests in `tests/test_strategy_composition_and_reporting.py`.
