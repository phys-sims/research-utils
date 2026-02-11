# research-utils

Shared research infrastructure for deterministic experimentation.

## Optional dependency extras

Install only the surfaces you need:

- `pip install research-utils[harness]`
- `pip install research-utils[ml]`
- `pip install research-utils[agent]`
- `pip install research-utils[all]`

`phys-pipeline` remains optional and adapter-scoped. Core modules in `research_utils.harness`,
`research_utils.ml`, and `research_utils.agents` must not require `phys-pipeline`; direct imports
are restricted to `research_utils.harness.adapters.phys_pipeline`.
