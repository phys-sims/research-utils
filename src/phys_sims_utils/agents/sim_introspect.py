"""Project/simulation introspection helpers with deterministic output."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class IntrospectionReport:
    """Deterministic introspection report for docs/tests hints."""

    doc_hints: tuple[str, ...]
    test_hints: tuple[str, ...]


def build_introspection_report(project_root: str | Path) -> IntrospectionReport:
    """Build stable hints by inspecting source and tests layout."""
    root = Path(project_root)
    src_root = root / "src" / "phys_sims_utils"
    tests_root = root / "tests"

    modules = sorted(path for path in src_root.rglob("*.py") if path.name != "__init__.py")
    tests = sorted(tests_root.rglob("test_*.py"))
    test_stems = {path.stem.removeprefix("test_") for path in tests}

    doc_hints = _build_doc_hints(modules=modules, root=root)
    test_hints = _build_test_hints(modules=modules, test_stems=test_stems, root=root)
    return IntrospectionReport(doc_hints=doc_hints, test_hints=test_hints)


def _build_doc_hints(*, modules: list[Path], root: Path) -> tuple[str, ...]:
    hints: list[str] = []
    for module_path in modules:
        functions, classes = _symbol_counts(module_path)
        rel = module_path.relative_to(root).as_posix()
        hints.append(
            f"Document module {rel}: classes={classes}, functions={functions}."
        )
    return tuple(hints)


def _build_test_hints(*, modules: list[Path], test_stems: set[str], root: Path) -> tuple[str, ...]:
    hints: list[str] = []
    for module_path in modules:
        module_stem = module_path.stem
        if module_stem in test_stems:
            continue
        rel = module_path.relative_to(root).as_posix()
        hints.append(f"Add tests for module {rel} (missing tests/test_{module_stem}.py).")
    return tuple(hints)


def _symbol_counts(module_path: Path) -> tuple[int, int]:
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    functions = 0
    classes = 0
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            functions += 1
        elif isinstance(node, ast.ClassDef):
            classes += 1
    return functions, classes


__all__ = ["IntrospectionReport", "build_introspection_report"]
