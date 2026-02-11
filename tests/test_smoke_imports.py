"""Smoke tests for stable import surfaces."""

from research_utils import (
    AgentArtifact,
    EvalResult,
    OptimizationRunner,
    ParameterSpace,
    TestHarness,
    agents,
    harness,
    ml,
    shared,
)
from research_utils.harness.plotting import ReportSpec
from research_utils.ml.strategies import RandomSearchStrategy


def test_package_roots_import() -> None:
    assert agents is not None
    assert harness is not None
    assert ml is not None
    assert shared is not None


def test_key_symbols_exported() -> None:
    assert AgentArtifact is not None
    assert EvalResult is not None
    assert ParameterSpace is not None
    assert OptimizationRunner is not None
    assert TestHarness is not None
    assert ReportSpec is not None
    assert RandomSearchStrategy is not None
