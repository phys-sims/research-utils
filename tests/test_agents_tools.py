"""Tests for deterministic agent tooling artifacts and checks."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sim_utils.agents import (
    ExperimentScriptSpec,
    ScriptProvenance,
    build_introspection_report,
    check_script_metadata,
    generate_experiment_script,
)

GOLDEN_DIR = Path(__file__).parent / "golden" / "agents"


def test_generate_experiment_script_matches_golden(tmp_path: Path) -> None:
    spec = ExperimentScriptSpec(
        name="baseline experiment",
        adapter_import="some_pkg.adapter",
        parameter_paths=("physics.beta", "physics.alpha"),
        base_config={"physics": {"beta": 2.0, "alpha": 1.5}},
    )
    output_path = generate_experiment_script(
        spec,
        output_dir=tmp_path / "experiments",
        generated_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        provenance=ScriptProvenance(package_version="0.0.0", git_commit="deadbeef"),
    )

    generated = output_path.read_text(encoding="utf-8")
    expected = (GOLDEN_DIR / "generated_experiment.py.golden").read_text(encoding="utf-8")

    assert output_path.parent.name == "experiments"
    assert generated == expected


def test_repo_checks_report_missing_seed_hash_and_invalid_paths() -> None:
    result = check_script_metadata(
        GOLDEN_DIR / "invalid_script.py",
        valid_parameter_paths={"physics.alpha", "physics.beta"},
    )

    codes = [issue.code for issue in result.issues]
    assert codes == [
        "missing-seed-policy",
        "missing-seed-argument",
        "missing-config-hash",
        "missing-provenance",
        "invalid-parameter-path",
    ]


def test_repo_checks_pass_for_generated_script(tmp_path: Path) -> None:
    spec = ExperimentScriptSpec(
        name="valid",
        adapter_import="some_pkg.adapter",
        parameter_paths=("physics.alpha",),
        base_config={"physics": {"alpha": 1.0}},
    )
    output_path = generate_experiment_script(
        spec,
        output_dir=tmp_path / "experiments",
        generated_at=datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        provenance=ScriptProvenance(package_version="0.0.0", git_commit="deadbeef"),
    )

    result = check_script_metadata(output_path, valid_parameter_paths={"physics.alpha"})

    assert result.issues == ()


def test_sim_introspection_report_is_deterministic() -> None:
    report_a = build_introspection_report(Path(__file__).resolve().parents[1])
    report_b = build_introspection_report(Path(__file__).resolve().parents[1])

    assert report_a == report_b
    assert all(
        hint.startswith("Document module src/sim_utils/")
        for hint in report_a.doc_hints
    )
