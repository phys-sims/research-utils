"""Deterministic repository checks for generated experiment artifacts."""

from __future__ import annotations

import ast
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RepoIssue:
    """Structured repository validation issue."""

    code: str
    message: str


@dataclass(frozen=True)
class RepoCheckResult:
    """Validation result for a single script file."""

    path: Path
    issues: tuple[RepoIssue, ...]


def check_script_metadata(
    script_path: str | Path,
    *,
    valid_parameter_paths: Iterable[str],
) -> RepoCheckResult:
    """Run script-level checks for seed/config/provenance and parameter path validity."""
    path = Path(script_path)
    source = path.read_text(encoding="utf-8")

    issue_list: list[RepoIssue] = []
    issue_list.extend(_check_missing_seeds(source))
    issue_list.extend(_check_missing_config_hash_or_provenance(source))
    issue_list.extend(_check_missing_structure_metadata(source))
    issue_list.extend(
        _check_invalid_parameter_paths(source, valid_paths=set(valid_parameter_paths))
    )

    return RepoCheckResult(path=path, issues=tuple(issue_list))


def _check_missing_seeds(source: str) -> list[RepoIssue]:
    issues: list[RepoIssue] = []
    if "# seed_policy:" not in source:
        issues.append(
            RepoIssue(
                code="missing-seed-policy",
                message="Missing '# seed_policy:' metadata header.",
            )
        )
    if "def main(*, seed: int)" not in source:
        issues.append(
            RepoIssue(
                code="missing-seed-argument",
                message="main must require an explicit 'seed' argument.",
            )
        )
    return issues


def _check_missing_config_hash_or_provenance(source: str) -> list[RepoIssue]:
    issues: list[RepoIssue] = []
    if "# config_hash:" not in source:
        issues.append(
            RepoIssue(
                code="missing-config-hash",
                message="Missing '# config_hash:' metadata header.",
            )
        )
    if "# provenance:" not in source:
        issues.append(
            RepoIssue(
                code="missing-provenance",
                message="Missing '# provenance:' metadata header.",
            )
        )
    return issues


def _check_missing_structure_metadata(source: str) -> list[RepoIssue]:
    if "# structure_fields:" not in source:
        return [
            RepoIssue(
                code="missing-structure-metadata",
                message="Missing '# structure_fields:' metadata header.",
            )
        ]
    return []


def _check_invalid_parameter_paths(source: str, *, valid_paths: set[str]) -> list[RepoIssue]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [RepoIssue(code="invalid-python", message="Script is not valid Python syntax.")]

    declared_paths = _extract_parameter_paths(tree)
    invalid_paths = sorted(path for path in declared_paths if path not in valid_paths)
    return [
        RepoIssue(
            code="invalid-parameter-path",
            message=f"Invalid parameter path declared: '{path}'.",
        )
        for path in invalid_paths
    ]


def _extract_parameter_paths(tree: ast.AST) -> tuple[str, ...]:
    if not isinstance(tree, ast.Module):
        return ()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "PARAMETER_PATHS":
                literal = ast.literal_eval(node.value)
                if isinstance(literal, tuple):
                    values = tuple(str(item) for item in literal)
                    return tuple(sorted(values))
    return ()


__all__ = ["RepoCheckResult", "RepoIssue", "check_script_metadata"]
