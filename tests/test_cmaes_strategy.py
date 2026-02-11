"""CMA-ES strategy tests."""

from __future__ import annotations

import importlib.util

import pytest

from research_utils.ml import Parameter, ParameterSpace
import research_utils.ml.strategies.cmaes as cmaes_module
from research_utils.ml.strategies.cmaes import CMAESStrategy
from research_utils.shared import EvalResult

requires_cma = pytest.mark.skipif(
    importlib.util.find_spec("cma") is None,
    reason="cma is not installed",
)


def test_cmaes_strategy_missing_dependency_error_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cmaes_module, "_cma", None)
    parameter_space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))

    with pytest.raises(RuntimeError, match="optional 'cma' package") as exc_info:
        CMAESStrategy(parameter_space=parameter_space, seed=3)

    assert "research-utils[ml]" in str(exc_info.value)


@requires_cma
def test_cmaes_strategy_is_reproducible_for_same_seed() -> None:
    parameter_space = ParameterSpace(
        parameters=(
            Parameter("x", bounds=(-1.0, 1.0)),
            Parameter("y", bounds=(0.0, 2.0)),
        )
    )

    strategy_a = CMAESStrategy(parameter_space=parameter_space, seed=17)
    strategy_b = CMAESStrategy(parameter_space=parameter_space, seed=17)

    asked_a = [strategy_a.ask().theta for _ in range(5)]
    asked_b = [strategy_b.ask().theta for _ in range(5)]

    assert asked_a == asked_b


@requires_cma
def test_cmaes_strategy_enforces_bounds_on_asked_candidates() -> None:
    parameter_space = ParameterSpace(
        parameters=(
            Parameter("x", bounds=(-2.0, -1.0)),
            Parameter("y", bounds=(10.0, 11.0)),
        )
    )
    strategy = CMAESStrategy(parameter_space=parameter_space, seed=5)

    for _ in range(25):
        theta = strategy.ask().theta
        assert -2.0 <= theta["x"] <= -1.0
        assert 10.0 <= theta["y"] <= 11.0


@requires_cma
def test_cmaes_strategy_tell_updates_history_and_convergence() -> None:
    parameter_space = ParameterSpace(parameters=(Parameter("x", bounds=(0.0, 1.0)),))
    strategy = CMAESStrategy(parameter_space=parameter_space, seed=9, max_iterations=3)

    for _ in range(3):
        theta = strategy.ask().theta
        objective = (theta["x"] - 0.3) ** 2
        strategy.tell(EvalResult(theta=theta, objective=objective))

    history = strategy.result
    assert len(history.evaluations) == 3
    assert history.best is not None
    assert history.best.objective == min(item.objective for item in history.evaluations)
    assert strategy.is_converged
