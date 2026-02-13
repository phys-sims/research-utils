# How to use the agent tooling

This page explains what is (and is not) "agentic" in `phys-sims-utils`, and how teams can use it
without writing a custom MCP server.

## TL;DR

- You **do not** need to write an MCP server to use the built-in agent tooling.
- The current UX is **library-first** (Python APIs and generated artifacts), not a full chat product UX.
- It is "agentic" in the sense that tools produce deterministic artifacts and validation reports that
  guide next actions.

## What the agent layer provides

The agent layer in `phys_sims_utils.agents` focuses on deterministic infrastructure tasks:

- **Experiment generation**: `generate_experiment_script(...)` writes a reproducible downstream script with
  seed policy, config hash, and provenance headers.
- **Repository/policy checks**: `check_script_metadata(...)` validates generated or hand-written scripts for
  reproducibility requirements (explicit seed, config hash, provenance, parameter-path validity).
- **Project introspection**: `build_introspection_report(...)` emits stable doc/test hints by scanning source
  and test layout.

These tools produce artifacts and structured outputs, and they avoid embedding domain-specific physics logic.

## Do I need MCP?

No, not for this repo's current agent tooling.

Use cases today:

1. **Direct Python usage** in your own scripts or notebooks.
2. **CI usage** where you generate scripts and run validation checks as quality gates.
3. **Wrapper usage** where a separate assistant framework (chat UI, orchestration layer, MCP host) calls
   these Python functions.

If your organization already uses MCP, you can add a thin MCP wrapper later, but it is optional.

## Does the UX make sense for non-coders?

Partially yes, with one caveat:

- ✅ Strong for reliability and auditability (clear artifacts, deterministic outputs, policy checks).
- ✅ Strong for technical operators (Python API + CI integration).
- ⚠️ Not yet a turnkey end-user GUI/chat flow in this repository.

A practical no-code-ish flow is:

1. Run a prepared command that calls `generate_experiment_script(...)`.
2. Run a prepared command that calls `check_script_metadata(...)`.
3. Review generated files and check output in plain-language templates.

This gives non-coders a guided workflow without asking them to write core logic.

## Is it really agentic?

Yes, in an infrastructure sense.

`phys-sims-utils` treats agents as deterministic tooling that:

- synthesizes structured artifacts,
- validates policy/contract compliance,
- and produces actionable next-step signals.

It deliberately does **not** include autonomous physics reasoning or hidden side effects.
That boundary is intentional and aligned with the project's architecture/ADR direction.

## Minimal usage example

```python
from datetime import datetime, timezone
from pathlib import Path

from phys_sims_utils.agents import (
    ExperimentScriptSpec,
    ScriptProvenance,
    check_script_metadata,
    generate_experiment_script,
)

spec = ExperimentScriptSpec(
    name="baseline experiment",
    adapter_import="some_pkg.adapter",
    parameter_paths=("physics.alpha", "physics.beta"),
    base_config={"physics": {"alpha": 1.5, "beta": 2.0}},
)

script_path = generate_experiment_script(
    spec,
    output_dir=Path("experiments"),
    generated_at=datetime.now(timezone.utc),
    provenance=ScriptProvenance(package_version="0.2.0", git_commit="<commit>"),
)

result = check_script_metadata(
    script_path,
    valid_parameter_paths={"physics.alpha", "physics.beta"},
)

print(script_path)
print(result.issues)
```
