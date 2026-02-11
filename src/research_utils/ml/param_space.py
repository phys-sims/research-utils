"""Parameter-space contracts with deterministic encode/decode behavior."""

from __future__ import annotations

from collections.abc import Callable, MutableMapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, is_dataclass
from typing import Any, Protocol


class ParameterTransform(Protocol):
    """Bidirectional scalar transform used during encode/decode."""

    def encode(self, value: float) -> float:
        """Transform a config-space value into optimizer-space."""

    def decode(self, value: float) -> float:
        """Transform an optimizer-space value into config-space."""


@dataclass(frozen=True)
class Parameter:
    """Parameter descriptor with optional path and transform."""

    name: str
    bounds: tuple[float, float]
    transform: ParameterTransform | tuple[Callable[[float], float], Callable[[float], float]] | None = None
    path: str | None = None

    def __post_init__(self) -> None:
        lower, upper = self.bounds
        if lower > upper:
            msg = f"Invalid bounds for '{self.name}': {self.bounds}"
            raise ValueError(msg)

    @property
    def resolved_path(self) -> str:
        """Dot path used for reading/writing this parameter."""
        return self.path if self.path is not None else self.name

    def to_encoded(self, value: float) -> float:
        """Convert config-space value to encoded optimizer value."""
        self.validate(value)
        if self.transform is None:
            return value
        if isinstance(self.transform, tuple):
            return self.transform[0](value)
        return self.transform.encode(value)

    def from_encoded(self, value: float) -> float:
        """Convert encoded optimizer value to config-space value."""
        if self.transform is None:
            decoded = value
        elif isinstance(self.transform, tuple):
            decoded = self.transform[1](value)
        else:
            decoded = self.transform.decode(value)
        self.validate(decoded)
        return decoded

    def validate(self, value: float) -> None:
        """Validate a config-space value against inclusive bounds."""
        lower, upper = self.bounds
        if value < lower or value > upper:
            msg = (
                f"Parameter '{self.name}' out of bounds: {value} not in "
                f"[{lower}, {upper}]"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class ParameterSpace:
    """Stable parameter-space contract with side-effect-safe updates."""

    parameters: tuple[Parameter, ...]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(parameter.name for parameter in self.parameters)

    def encode(self, config: Any) -> tuple[float, ...]:
        """Encode config object values in parameter order."""
        return tuple(
            parameter.to_encoded(float(_get_by_path(config, parameter.resolved_path)))
            for parameter in self.parameters
        )

    def decode(self, encoded: Sequence[float], base: Any | None = None) -> Any:
        """Decode encoded vector into a new config object.

        ``base`` is deep-copied before updates so decode is side-effect safe.
        """
        if len(encoded) != len(self.parameters):
            msg = (
                "Encoded vector length mismatch: "
                f"expected {len(self.parameters)}, got {len(encoded)}"
            )
            raise ValueError(msg)

        config: Any = deepcopy(base) if base is not None else {}
        for index, parameter in enumerate(self.parameters):
            value = parameter.from_encoded(float(encoded[index]))
            config = _set_by_path(config, parameter.resolved_path, value)
        return config


def _get_by_path(obj: Any, path: str) -> Any:
    current = obj
    for segment in path.split("."):
        current = _get_segment(current, segment)
    return current


def _set_by_path(obj: Any, path: str, value: Any) -> Any:
    parts = path.split(".")
    if not parts:
        msg = "Path must not be empty"
        raise ValueError(msg)

    if obj is None:
        root: Any = {}
    else:
        root = obj

    current = root
    for segment in parts[:-1]:
        next_obj = _try_get_segment(current, segment)
        if next_obj is None:
            next_obj = {}
            _assign_segment(current, segment, next_obj)
        current = next_obj

    _assign_segment(current, parts[-1], value)
    return root


def _get_segment(obj: Any, segment: str) -> Any:
    if isinstance(obj, MutableMapping):
        return obj[segment]
    if hasattr(obj, segment):
        return getattr(obj, segment)
    msg = f"Could not resolve segment '{segment}' on {type(obj).__name__}"
    raise KeyError(msg)


def _try_get_segment(obj: Any, segment: str) -> Any | None:
    if isinstance(obj, MutableMapping):
        return obj.get(segment)
    if hasattr(obj, segment):
        return getattr(obj, segment)
    return None


def _assign_segment(obj: Any, segment: str, value: Any) -> None:
    if isinstance(obj, MutableMapping):
        obj[segment] = value
        return

    if is_dataclass(obj):
        setattr(obj, segment, value)
        return

    if hasattr(obj, segment) or hasattr(obj, "__dict__"):
        setattr(obj, segment, value)
        return

    msg = f"Could not assign segment '{segment}' on {type(obj).__name__}"
    raise KeyError(msg)


__all__ = ["Parameter", "ParameterSpace", "ParameterTransform"]
