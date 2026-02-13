# Project Status (phys-sims-utils)

> **Source of truth:** Update this file whenever behavior, contracts, tests, CI, or roadmap state changes.
>
> **IMPORTANT (for agents):**
> - When updating dates or timestamps in this file, **always use the system clock**.
> - Use `date` or `date -u` (or the platform-equivalent) to obtain the current date/time.
> - **Do not guess or infer dates.** Incorrect dates are considered a documentation error.
>
> This file is written for **agents**. Be concrete, factual, and current.

---

## Current release snapshot

- **Current package version:** `0.3.0`
- **Roadmap state:** v0.2 complete; v0.3 complete on 2026-02-13; v0.4 scope ratified on 2026-02-13
- **Release notes:** `docs/releases/v0.3.0.md`

---

## CI health checklist

| Check | Command | Status | Last run | Notes |
| --- | --- | --- | --- | --- |
| Pre-commit (lint/format) | `python -m pre_commit run -a` | ✅ | 2026-02-13 | Passed locally after v0.3 implementation + release updates. |
| Type checking (mypy) | `python -m mypy src tests` | ✅ | 2026-02-13 | Strict mode passes for harness, ML, and agent tooling surfaces. |
| Pytest fast | `python -m pytest -q -m "not slow" --durations=10` | ✅ | 2026-02-13 | Includes deterministic agent tooling, composition, and reporting schema-lock coverage. |
| Pytest slow | `python -m pytest -q -m slow --durations=10` | ⬜ | YYYY-MM-DD |  |

Rules:
- CI **must be green** before merging.
- If a change breaks CI, fix it in the same PR.
- Record real run dates and real notes (do not guess).

---

## Test suites (definitions, runtimes, slowest tests)

| Suite | Definition | Typical runtime | Slowest tests (top 3) | Last measured | Notes |
| --- | --- | --- | --- | --- | --- |
| Fast | `-m "not slow" --durations=10` | TBD | TBD | 2026-02-11 | Includes plotting helper tests for non-interactive backend configuration and output artifact generation (skipped when matplotlib is unavailable). |
| Slow | `-m slow --durations=10` | TBD | TBD | YYYY-MM-DD |  |
| Full | `-m "slow or not slow" --durations=10` | TBD | TBD | YYYY-MM-DD |  |

Guidelines:
- Keep fast tests fast.
- If a test becomes slow, mark it explicitly.
- Note regressions in runtime here.

---

## Contract status (infrastructure APIs)

### Canonical data models
Record the **current authoritative shapes**.

| Contract | Status | Notes |
| --- | --- | --- |
| `EvalResult` | ✅ | Canonical shape exercised by contract tests and end-to-end dummy example artifacts. |
| `SweepResult` | ✅ | CSV persistence and canonical plotting consumption validated in deterministic sweep and end-to-end tests. |
| `OptimizationHistory` | ✅ | Best-so-far semantics now exercised through OptimizationRunner tests (including penalty and batching paths). |
| `Parameter` | ✅ | Bounds + transform behavior validated via new contract tests. |
| `ParameterSpace` | ✅ | Deterministic encode/decode with nested path assignment and side-effect-safe decode tested. |
| `OptimizerStrategy` | ✅ | ask/tell flow validated via RandomStrategy + OptimizationRunner integration tests. |

Any breaking change to these requires:
- ADR
- version bump
- STATUS.md update

---

## Adapter status

### phys-pipeline adapter

| Item | Status | Notes |
| --- | --- | --- |
| Adapter exists (`harness.adapters.phys_pipeline`) | ✅ | `PhysPipelineAdapter` accepts pipeline instance or factory. |
| Optional dependency only | ✅ | `phys-pipeline` import is lazy and only required for default pipeline construction. |
| Deterministic seeding verified | ✅ | Tested with seed-stable dummy pipeline behavior. |
| Metric extraction tested | ✅ | Objective and extra metrics are validated through extractor callbacks. |
| No sim-specific assumptions leaked | ✅ | Adapter only maps config/output to canonical `EvalResult`. |

---

## Harness feature checklist

| Feature | Status | Notes |
| --- | --- | --- |
| `SweepSpec` (grid) | ✅ | Used for deterministic sweep generation in harness and end-to-end example. |
| `SweepSpec` (random) | ✅ | Deterministic random ordering validated with fixed seeds. |
| `SweepSpec` (sobol) | ✅ | Optional scipy-backed path implemented with guarded dependency behavior. |
| `MetricSpec` | ✅ | Metric computation/aggregation flow exercised in harness unit coverage. |
| Deterministic sweep ordering | ✅ | Same seed reproducibility verified for sampled points and sweep outputs. |
| Result persistence (CSV/Parquet) | ✅ | CSV export validated in tests; parquet path supported when pandas backend is available. |
| Canonical plots available | ✅ | Added canonical sweep plotting helpers (1D objective slice, 2D objective heatmap, metric-vs-metric scatter) and optimization convergence plotting over canonical result contracts. |

---

## ML / optimization checklist

| Feature | Status | Notes |
| --- | --- | --- |
| `SimulationEvaluator` | ✅ | Adapter-backed evaluator now returns objective and metrics deterministically. |
| `RandomStrategy` | ✅ | Always-available deterministic uniform sampling strategy implemented and tested for seed reproducibility. |
| `SobolStrategy` | ✅ | Implemented behind SciPy import guard; raises a clear runtime error when SciPy is unavailable. |
| `CMAESStrategy` | ✅ | Implemented behind `cma` import guard with deterministic seeding and bound-constrained ask/tell behavior. |
| Constraint handling | ✅ | Deterministic penalty objective path is integrated in `OptimizationRunner` with tests locking failure-to-penalty conversion behavior. |
| Strategy composition | ✅ | Added deterministic `StagedStrategy` and `PortfolioStrategy` under shared `OptimizerStrategy` ask/tell contract. |
| Deterministic logging | ✅ | JSONL/CSV logger with run metadata and best-so-far snapshots integrated with OptimizationRunner. |

---

## Agentic tooling checklist

| Tool | Status | Notes |
| --- | --- | --- |
| Experiment script generator | ✅ | Deterministic generation to `experiments/` with metadata headers (timestamp, seed policy, config hash, provenance). |
| Repo structure validator | ✅ | Checks for missing seed policy/seed argument, missing config hash/provenance metadata, and invalid parameter paths. |
| Simulation introspection | ✅ | Deterministic project introspection emits documentation and test-coverage hints without physics assumptions. |
| Golden-file tests | ✅ | Added golden-file coverage for generated script output format stability. |

Agents must produce **artifacts**, not side effects.

---

## Determinism & provenance checklist

| Requirement | Status | Notes |
| --- | --- | --- |
| Explicit seed required | ✅ | Public harness/runner entrypoints require or derive explicit seeds in tests and docs. |
| Config hashing implemented | ✅ | Harness computes stable SHA256 hash for base config and persists it in results. |
| Provenance recorded | ✅ | Sweep/optimization metadata artifacts include run-level provenance and seed fields. |
| Determinism tests exist | ✅ | Deterministic sweep and strategy repeatability tests lock same-input behavior. |

If determinism cannot be guaranteed, document and justify in an ADR.

---

## ADR checklist

| Area | ADR exists? | Notes |
| --- | --- | --- |
| Core contracts | ✅ | ADR 0001 documents canonical shared result contracts; ADR 0007 extends ParameterSpace for mixed numeric/categorical search. |
| Dependency boundaries | ✅ | ADR 0002 defines optional extras and adapter-scoped simulator dependencies. |
| Determinism policy | ✅ | ADR 0003 formalizes explicit seed requirements and deterministic derivation policy. |
| Result storage format | ✅ | ADR 0005 defines canonical deterministic run-summary JSON artifacts for sweep/optimization reporting helpers. |
| Optimization interfaces | ✅ | ADR 0004 documents staged/portfolio composition semantics on top of shared ask/tell contracts. |
| Agent responsibilities | ✅ | ADR 0006 documents agent scope limits, artifact-only behavior, and reproducibility guardrails. |

---

## Roadmap / release checklist

Execution planning reference:
- `docs/v0.2-action-plan.md` captures the execution-ready 6-sprint v0.2 action plan,
  work-package sequencing, and release-readiness gates.
- `docs/v0.3-roadmap.md` captures the planned milestones for mixed-parameter optics
  optimization workflows and lab onboarding.
- `docs/v0.4-roadmap.md` captures planned agent-first workflows for low-friction lab usage.

### v0.1 — Minimal research-usable core
Status: ✅ Complete (all checklist items green as of 2026-02-11).
- [x] Harness core usable in private testbench
- [x] phys-pipeline adapter stable
- [x] ParameterSpace encode/decode locked
- [x] Random + Sobol strategies
- [x] Canonical plots implemented
- [x] CI consistently green
- [x] ADRs written for all core decisions
- [x] Ready for first PyPI release

### v0.2 — Optimization composition + agents
Status: ✅ Complete (all roadmap commitments shipped and validated on 2026-02-12).
- [x] CMA-ES (optional)
- [x] Strategy composition
- [x] Agent experiment generators
- [x] Validation agents
- [x] Improved reporting

### v0.3 — Mixed-parameter optics optimization workflows
Status: ✅ Complete (all roadmap commitments shipped and validated on 2026-02-13).
- [x] Mixed continuous + discrete/categorical `ParameterSpace` contract extension
- [x] Deterministic topology-aware optimization runs (component add/remove decisions)
- [x] Canonical summary/reporting schema updates for structure metadata
- [x] Agent tooling templates and validators for mixed-parameter experiments
- [x] Lab onboarding quickstart and release-readiness closure

### v0.4 — Agent-first low-friction lab workflows
Status: 🟨 Planned (scope ratified on 2026-02-13; implementation not started).
- [ ] Agent workflow contracts for adaptation, optimization advisory, and graphics intents
- [ ] Deterministic repository adaptation assistant artifacts and validators
- [ ] Deterministic optimization strategy advisor with rationale + fallback outputs
- [ ] Chat-oriented graphics/reporting concierge over canonical result contracts
- [ ] Human + agent onboarding documentation synchronized with ADR and STATUS state

---

## Known issues
List concrete, reproducible issues only.

- None recorded.

---

## Next actions
Short, concrete, actionable items.

- [x] Deliver v0.2 Milestone 1 (ADR closure + roadmap/status reconciliation) from `docs/v0.2-action-plan.md`.
- [x] Deliver v0.2 Milestone 2 (constraint handling v1) with deterministic penalty/feasibility tests.
- [x] Deliver v0.2 Milestone 3 (staged + portfolio composition) behind shared strategy contracts.
- [x] Deliver v0.2 Milestone 4 (canonical reporting improvements and artifact schema lock tests).
- [x] Execute v0.2 release readiness checklist and version/release-note synchronization.
- [x] Define and ratify v0.3 roadmap scope (post-v0.2 follow-up).
- [x] Start v0.3 Milestone 1 (mixed-parameter contract extension + ADR + tests).
- [ ] Start v0.4 Milestone 1 (agent workflow contracts and validation artifacts).
