# Project Status (research-utils)

> **Source of truth:** Update this file whenever behavior, contracts, tests, CI, or roadmap state changes.
>
> **IMPORTANT (for agents):**
> - When updating dates or timestamps in this file, **always use the system clock**.
> - Use `date` or `date -u` (or the platform-equivalent) to obtain the current date/time.
> - **Do not guess or infer dates.** Incorrect dates are considered a documentation error.
>
> This file is written for **agents**. Be concrete, factual, and current.

---

## CI health checklist

| Check | Command | Status | Last run | Notes |
| --- | --- | --- | --- | --- |
| Pre-commit (lint/format) | `python -m pre_commit run -a` | ✅ | 2026-02-11 | Passed locally after ML parameter-space/evaluator and test updates. |
| Type checking (mypy) | `python -m mypy src tests` | ✅ | 2026-02-11 | Strict mode passes. |
| Pytest fast | `python -m pytest -q -m "not slow" --durations=10` | ✅ | 2026-02-11 | Includes parameter-space round-trip/bounds/path tests and simulation evaluator coverage. |
| Pytest slow | `python -m pytest -q -m slow --durations=10` | ⬜ | YYYY-MM-DD |  |

Rules:
- CI **must be green** before merging.
- If a change breaks CI, fix it in the same PR.
- Record real run dates and real notes (do not guess).

---

## Test suites (definitions, runtimes, slowest tests)

| Suite | Definition | Typical runtime | Slowest tests (top 3) | Last measured | Notes |
| --- | --- | --- | --- | --- | --- |
| Fast | `-m "not slow" --durations=10` | TBD | TBD | YYYY-MM-DD |  |
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
| `EvalResult` | ⬜ | Defined / tested / stable? |
| `SweepResult` | ⬜ | Serialization format decided? |
| `OptimizationHistory` | ⬜ | Best-so-far semantics locked? |
| `Parameter` | ✅ | Bounds + transform behavior validated via new contract tests. |
| `ParameterSpace` | ✅ | Deterministic encode/decode with nested path assignment and side-effect-safe decode tested. |
| `OptimizerStrategy` | ⬜ | ask/tell semantics finalized? |

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
| `SweepSpec` (grid) | ⬜ |  |
| `SweepSpec` (random) | ⬜ |  |
| `SweepSpec` (sobol) | ⬜ | Optional dependency |
| `MetricSpec` | ⬜ | Error metrics defined |
| Deterministic sweep ordering | ⬜ | Same seed ⇒ same order |
| Result persistence (CSV/Parquet) | ⬜ | Format decision documented |
| Canonical plots available | ⬜ | 1D, 2D, convergence |

---

## ML / optimization checklist

| Feature | Status | Notes |
| --- | --- | --- |
| `SimulationEvaluator` | ✅ | Adapter-backed evaluator now returns objective and metrics deterministically. |
| `RandomStrategy` | ⬜ | Baseline |
| `SobolStrategy` | ⬜ | Optional dependency |
| `CMAESStrategy` | ⬜ | Optional dependency |
| Constraint handling | ⬜ | Penalties / feasibility |
| Strategy composition | ⬜ | Pipeline / portfolio |
| Deterministic logging | ⬜ | Best-so-far tracked |

---

## Agentic tooling checklist

| Tool | Status | Notes |
| --- | --- | --- |
| Experiment script generator | ⬜ | Deterministic output |
| Repo structure validator | ⬜ | Seeds, hashes, metadata |
| Simulation introspection | ⬜ | No physics logic |
| Golden-file tests | ⬜ | Required for generators |

Agents must produce **artifacts**, not side effects.

---

## Determinism & provenance checklist

| Requirement | Status | Notes |
| --- | --- | --- |
| Explicit seed required | ⬜ | No hidden RNG |
| Config hashing implemented | ⬜ | Stable across runs |
| Provenance recorded | ⬜ | Versions, git commit |
| Determinism tests exist | ⬜ | Same inputs ⇒ same outputs |

If determinism cannot be guaranteed, document and justify in an ADR.

---

## ADR checklist

| Area | ADR exists? | Notes |
| --- | --- | --- |
| Core contracts | ⬜ | EvalResult, SweepResult |
| Dependency boundaries | ⬜ | Optional extras |
| Determinism policy | ⬜ | RNG derivation |
| Result storage format | ⬜ | CSV vs Parquet |
| Optimization interfaces | ⬜ | ask/tell semantics |
| Agent responsibilities | ⬜ | Limits enforced |

---

## Roadmap / release checklist

### v0.1 — Minimal research-usable core
- [ ] Harness core usable in private testbench
- [ ] phys-pipeline adapter stable
- [ ] ParameterSpace encode/decode locked
- [ ] Random + Sobol strategies
- [ ] Canonical plots implemented
- [ ] CI consistently green
- [ ] ADRs written for all core decisions
- [ ] Ready for first PyPI release

### v0.2 — Optimization composition + agents
- [ ] CMA-ES (optional)
- [ ] Strategy composition
- [ ] Agent experiment generators
- [ ] Validation agents
- [ ] Improved reporting

---

## Known issues
List concrete, reproducible issues only.

- None recorded.

---

## Next actions
Short, concrete, actionable items.

- [ ] Bootstrap repo skeleton and CI.
- [ ] Implement EvalResult + SweepResult contracts.
- [ ] Write ADR for core data model.
- [ ] Add first deterministic sweep test.
- [ ] Update this file after first green CI run.
