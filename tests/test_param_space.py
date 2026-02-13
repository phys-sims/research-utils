"""Contract tests for Parameter/ParameterSpace behavior."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from phys_sims_utils.ml import Parameter, ParameterSpace


@dataclass
class InnerConfig:
    alpha: float = 0.0


@dataclass
class OuterConfig:
    inner: InnerConfig = field(default_factory=InnerConfig)


class PydanticLike:
    def __init__(self, value: float = 0.0) -> None:
        self.value = value


class ContainerLike:
    def __init__(self) -> None:
        self.model = PydanticLike()


def test_parameter_space_round_trip_with_transform_is_deterministic() -> None:
    parameter_space = ParameterSpace(
        parameters=(
            Parameter(
                name="alpha",
                bounds=(1.0, 16.0),
                path="optimizer.alpha",
                transform=(math.log2, lambda value: 2.0**value),
            ),
            Parameter(name="beta", bounds=(0.0, 1.0), path="optimizer.beta"),
        )
    )

    config = {"optimizer": {"alpha": 8.0, "beta": 0.25}}

    encoded = parameter_space.encode(config)
    decoded = parameter_space.decode(encoded, base=config)

    assert encoded == (3.0, 0.25)
    assert decoded == config
    assert decoded is not config


def test_bounds_validation_for_encode_and_decode() -> None:
    parameter_space = ParameterSpace(parameters=(Parameter("alpha", bounds=(0.0, 1.0)),))

    try:
        parameter_space.encode({"alpha": 2.0})
        raise AssertionError("Expected encode to fail for out-of-bounds value")
    except ValueError as exc:
        assert "out of bounds" in str(exc)

    try:
        parameter_space.decode((2.0,))
        raise AssertionError("Expected decode to fail for out-of-bounds value")
    except ValueError as exc:
        assert "out of bounds" in str(exc)


def test_nested_path_assignment_correctness() -> None:
    cases: list[tuple[object, str, object]] = [
        ({"a": {"b": 1.0}}, "a.b", {"a": {"b": 2.0}}),
        (OuterConfig(), "inner.alpha", 2.0),
        (ContainerLike(), "model.value", 2.0),
    ]

    for base, path, expected in cases:
        parameter_space = ParameterSpace(
            parameters=(Parameter(name="alpha", bounds=(0.0, 3.0), path=path),)
        )

        updated = parameter_space.decode((2.0,), base=base)

        if isinstance(base, dict):
            assert updated == expected
            assert base == {"a": {"b": 1.0}}
        elif isinstance(base, OuterConfig):
            assert isinstance(updated, OuterConfig)
            assert updated.inner.alpha == expected
            assert base.inner.alpha == 0.0
        else:
            assert isinstance(updated, ContainerLike)
            assert isinstance(base, ContainerLike)
            assert updated.model.value == expected
            assert base.model.value == 0.0
