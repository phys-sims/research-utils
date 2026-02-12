from __future__ import annotations

import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest


def _load_run_example() -> Callable[[Path], dict[str, Path]]:
    module_path = Path(__file__).resolve().parents[1] / "examples" / "dummy_end_to_end.py"
    spec = importlib.util.spec_from_file_location("dummy_end_to_end", module_path)
    if spec is None or spec.loader is None:
        msg = "Failed to load dummy_end_to_end example module"
        raise RuntimeError(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return cast(Callable[[Path], dict[str, Path]], module.run_example)


def test_dummy_end_to_end_example_generates_expected_artifacts(tmp_path: Path) -> None:
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg", force=True)

    run_example = _load_run_example()
    output_dir = tmp_path / "dummy_e2e"
    artifacts = run_example(output_dir)

    expected_keys = {
        "sweep_table",
        "heatmap",
        "metric_scatter",
        "convergence",
        "metadata",
        "optimizer_metadata",
    }
    assert set(artifacts) == expected_keys

    for artifact_path in artifacts.values():
        assert artifact_path.exists()
        assert artifact_path.stat().st_size > 0

    sweep_table = artifacts["sweep_table"].read_text(encoding="utf-8").strip().splitlines()
    assert len(sweep_table) == 10
    assert "theta.alpha" in sweep_table[0]
    assert "theta.beta" in sweep_table[0]

    metadata = json.loads(artifacts["metadata"].read_text(encoding="utf-8"))
    assert metadata["seed"] == 21
    assert metadata["sweep_size"] == 9
    assert metadata["optimization_evaluations"] == 8
    assert metadata["best_objective"] is not None
    assert isinstance(metadata["sweep_config_hash"], str)
    assert len(metadata["sweep_config_hash"]) == 64

    optimizer_metadata = json.loads(
        artifacts["optimizer_metadata"].read_text(encoding="utf-8")
    )
    assert optimizer_metadata["seed"] == 21
    assert optimizer_metadata["strategy"] == "random"
