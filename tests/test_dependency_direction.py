"""Static dependency-direction checks for package boundaries."""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "phys_sims_utils"


def _module_from_file(path: Path) -> str:
    rel = path.relative_to(SRC_ROOT.parent)
    return ".".join(rel.with_suffix("").parts)


def _imports_for_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: list[str] = []

    module = _module_from_file(path)
    package = module.rsplit(".", 1)[0] if "." in module else module

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue
            if node.level > 0:
                imported_module = package
                for _ in range(node.level - 1):
                    imported_module = imported_module.rsplit(".", 1)[0]
                if node.module:
                    imported_module = f"{imported_module}.{node.module}"
                imports.append(imported_module)
            else:
                imports.append(node.module)
    return imports


def test_harness_does_not_import_agents() -> None:
    violations: list[str] = []
    for path in (SRC_ROOT / "harness").rglob("*.py"):
        imports = _imports_for_file(path)
        if any(
            name == "phys_sims_utils.agents" or name.startswith("phys_sims_utils.agents.")
            for name in imports
        ):
            violations.append(str(path.relative_to(SRC_ROOT.parent)))

    assert not violations, f"harness importing agents in: {violations}"


def test_phys_pipeline_import_isolated_to_adapter_module() -> None:
    violations: list[str] = []
    allowed = "phys_sims_utils/harness/adapters/phys_pipeline.py"

    for path in SRC_ROOT.rglob("*.py"):
        imports = _imports_for_file(path)
        if any(name == "phys_pipeline" or name.startswith("phys_pipeline.") for name in imports):
            rel = str(path.relative_to(SRC_ROOT.parent))
            if rel != allowed:
                violations.append(rel)

    assert not violations, f"phys_pipeline imports outside allowed adapter: {violations}"
