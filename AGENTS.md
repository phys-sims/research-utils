# AGENTS

## Scope
This file applies to the entire repository unless a more specific `AGENTS.md` exists in a subdirectory.

This repository, **phys-sims-utils**, provides **shared research infrastructure** for physics simulations and optimization workflows. It is designed to be used by:
- simulation libraries that wrap `phys-pipeline` (e.g. `cpa-sim`, `abcdef-sim`)
- private research/testbench repos (e.g. `abcdef-testbench`)
- agentic tools that generate experiments, validate structure, or assist optimization

This repo does **not** own physics truth.  
It owns **reproducible experimentation, evaluation, optimization, and tooling**.

---

## Operating principles

### 1) Contract-first infrastructure
All major components expose **explicit, typed contracts**:
- evaluation inputs → evaluation outputs
- parameter spaces → encoded vectors → decoded configs
- sweeps / optimizations → structured results

Once a contract is public, it is considered **API**.
Breaking changes require:
- an ADR
- version bump
- roadmap update

### 2) Deterministic by default
Same inputs + same seed ⇒ same outputs (within defined tolerances).

No hidden randomness.
No implicit global RNGs.
Seeds, hashes, versions, and provenance are **first-class data**.

### 3) Thin adapters, thick core
Simulation-specific logic lives behind **adapters**.
The harness, ML layer, and agent tools remain **simulation-agnostic**.

If adapting `phys-pipeline`, keep all assumptions isolated in
`phys_sims_utils.harness.adapters`.

### 4) Infrastructure > novelty
Favor:
- clarity
- reproducibility
- testability
- composability

over clever abstractions or premature optimization.

---

## Key references (must read first)
- `STATUS.md` — current repo state, priorities, known gaps, and next milestones
- `docs/adr/` — architectural decisions and rationale
- `docs/how-to-use-harness.md`
- `docs/how-to-add-optimizer.md`
- `docs/how-to-write-adapter.md`
- `pyproject.toml` — extras, dependency boundaries, versioning

Agents should **read STATUS.md and ADRs before making changes**.

---

## End-goal acceptance criteria
Work iteratively across sessions until **all** of the following are true:

1) The test harness can:
   - run large parameter sweeps deterministically
   - compute objective + error metrics
   - save results in a stable, analyzable format
   - generate canonical plots with minimal user code

2) The ML layer provides:
   - a stable `ParameterSpace` encode/decode contract
   - multiple optimization strategies behind a shared interface
   - the ability to combine strategies (staged / portfolio / hybrid)
   - deterministic logging and “best-so-far” tracking

3) Agentic tools:
   - generate experiment scripts/configs deterministically
   - validate repo structure and reproducibility guarantees
   - assist development **without embedding physics logic**

4) CI is always green:
   - linting, typing, and tests pass
   - no broken main branch
   - no undocumented behavior drift

5) Documentation stays synchronized:
   - ADRs reflect reality
   - STATUS.md reflects current state
   - roadmaps match actual implementation progress

---

## Repository boundaries and responsibilities

### This repo owns:
- test harness + sweep orchestration
- metric definitions and aggregation
- parameter-space modeling
- optimization runners and strategies
- deterministic logging + provenance
- agentic tooling for experiment generation and validation
- shared utilities (I/O, RNG, errors, types)

### This repo does NOT own:
- physics models
- simulation correctness
- domain-specific validation

Simulation libraries and testbenches remain the source of physics truth.

---

## Architecture overview

### Harness layer
- `TestHarness`
- `SweepSpec`, `MetricSpec`, `ReportSpec`
- adapters for external simulators (e.g. phys-pipeline)

The harness produces **canonical result objects** consumed by plotting, ML, and agents.

### ML layer
- `Parameter`, `ParameterSpace`
- `SimulationEvaluator`
- `OptimizerStrategy` (ask/tell)
- `OptimizationRunner`
- constraints and penalties

All strategies must conform to the same interface so they can be composed.

### Agent layer
- experiment/script generators
- repo and policy validators
- simulation introspection tools
- prompt templates (not LLM calls embedded in core logic)

Agents produce **artifacts**, not side effects.

---

## Canonical data models (must remain stable)

### EvalResult
Single evaluation record:
- parameters (theta or dict)
- objective scalar
- metrics dict
- optional artifacts
- seed, config hash, timestamps
- provenance (versions, git commit)

### SweepResult / OptimizationHistory
Collections of `EvalResult` plus:
- ParameterSpace metadata
- base config metadata
- run-level provenance

All plotting, ML, and reporting must consume these types.

---

## Determinism / RNG rules
- Every public entrypoint requires an explicit seed (unless explicitly overridden).
- RNG derivation must be explicit and testable.
- Tests must confirm repeatability of key outputs.

If determinism cannot be guaranteed, document it clearly and justify in an ADR.

---

## Tests (required)

### Contract tests
- ParameterSpace encode/decode round-trips
- Adapter output conforms to EvalResult
- Result containers serialize/deserialize correctly

### Determinism tests
- Same inputs + same seed ⇒ identical results

### Integration tests
- End-to-end sweep or optimization with a dummy simulator
- Assert structure, ordering, and metadata integrity

### Proof-of-decision tests
Whenever a design choice is made (e.g. logging format, constraint handling, plotting defaults), add a small test that locks the behavior.

Keep tests fast. Use minimal dummy simulations.

---

## Documentation via ADRs (required)
Use ADRs in `docs/adr/` for:
- core contracts and data models
- dependency boundaries and extras
- determinism policy
- optimization strategy interfaces
- agent responsibilities and limits
- result storage formats

Each ADR must state:
- the decision
- alternatives considered
- consequences
- how the decision is validated (tests)

---

## STATUS.md (mandatory)
`STATUS.md` must always reflect reality.

Update it when:
- behavior changes
- APIs evolve
- tests are added/removed
- roadmap milestones shift

It should include:
- current version
- active focus
- known limitations
- next planned milestones (e.g. v0.1, v0.2 PyPI releases)

Use real dates. Do not guess.

---

## Roadmaps and releases
- Maintain a clear roadmap for upcoming versions (especially PyPI releases).
- Major milestones should be documented either in `STATUS.md` or a dedicated roadmap section.
- Breaking changes require:
  - ADR
  - version bump
  - clear release notes

---

## Developer workflow (CI must stay green)

### Required checks (must pass before PR)
- **Lint / format**
python -m pre_commit run -a

- **Type checking**
python -m mypy src tests

- **Tests**
pytest -q -m "not slow"

### Rules
- Never merge failing CI.
- Fix failures in the same PR that introduced them.
- Prefer the smallest change that restores green CI.
- Document non-trivial fixes via ADR or PR notes.
- Keep docs and code in sync.

### Pytest markers
- Fast tests (default): `-m "not slow"`
- Slow tests: `-m slow`
- Full suite: `-m "slow or not slow"`

---

## Guardrails
- Do not leak simulation-specific assumptions into core infrastructure.
- Avoid hidden global state.
- Prefer explicit configuration over magic defaults.
- Never silently ignore invalid inputs.
- Never change public contracts without ADR + versioning.