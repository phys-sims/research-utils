# ADR 0008: Agent workflow contracts for adaptation, advisory, and graphics intents

- Status: Accepted
- Date: 2026-02-13

## Decision

Introduce explicit request/response contracts and deterministic artifact manifests for v0.4
agent workflows in `phys_sims_utils.agents.workflows`:

- Adaptation assistant contract for deterministic repository findings + checklist artifacts.
- Strategy advisor contract for deterministic optimization recommendations + fallback records.
- Graphics concierge contract for structured intent-driven summary/plot generation.
- Shared `AgentArtifactManifest` contract across all workflows.
- Structured `AgentWorkflowError` contract for invalid requests and unsupported intents.

## Alternatives considered

1. Keep using ad-hoc dictionaries and function signatures per tool.
2. Put chat prompt text/provider details directly into workflow contracts.
3. Add simulator-specific recommendation logic in shared advisor code.

All alternatives were rejected to preserve deterministic machine-readable contracts,
repository boundary rules, and simulation-agnostic behavior.

## Consequences

- Agent workflows are now contract-first and composable for chat wrappers/CI automation.
- Artifact manifests provide a stable integration point for downstream orchestration.
- Unsupported workflows fail with structured actionable errors instead of silent drift.

## Validation

- Contract + determinism + integration tests in `tests/test_agent_workflows_v04.py`.
- Existing agent-tooling compatibility remains covered by `tests/test_agents_tools.py`.
