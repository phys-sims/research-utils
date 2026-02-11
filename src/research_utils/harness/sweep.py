"""Sweep specifications and deterministic sampling utilities."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import random
from typing import Literal

SamplingMode = Literal["grid", "random", "sobol"]


@dataclass(frozen=True)
class ParameterRange:
    """Inclusive lower/upper bounds for a scalar parameter."""

    lower: float
    upper: float

    def validate(self) -> None:
        if self.upper < self.lower:
            msg = f"invalid range: upper ({self.upper}) < lower ({self.lower})"
            raise ValueError(msg)


@dataclass(frozen=True)
class SweepSpec:
    """Typed sweep specification used by :class:`~research_utils.harness.core.TestHarness`."""

    parameters: dict[str, ParameterRange]
    mode: SamplingMode = "grid"
    n_samples: int = 16
    grid_points: int = 3
    allow_unseeded: bool = False

    def ordered_parameter_names(self) -> tuple[str, ...]:
        return tuple(sorted(self.parameters))


def _linspace(lower: float, upper: float, points: int) -> list[float]:
    if points <= 0:
        raise ValueError("grid_points must be > 0")
    if points == 1:
        return [lower]
    step = (upper - lower) / (points - 1)
    return [lower + i * step for i in range(points)]


def sample_points(spec: SweepSpec, seed: int | None) -> list[dict[str, float]]:
    """Return deterministic candidate points in stable parameter order."""
    for parameter in spec.parameters.values():
        parameter.validate()

    if seed is None and not spec.allow_unseeded:
        raise ValueError("seed is required unless allow_unseeded=True")

    names = spec.ordered_parameter_names()
    ranges = [spec.parameters[name] for name in names]

    if spec.mode == "grid":
        per_dimension = [_linspace(r.lower, r.upper, spec.grid_points) for r in ranges]
        return [
            {name: value for name, value in zip(names, values, strict=True)}
            for values in product(*per_dimension)
        ]

    rng = random.Random(seed)
    if spec.mode == "random":
        points: list[dict[str, float]] = []
        for _ in range(spec.n_samples):
            points.append({name: rng.uniform(r.lower, r.upper) for name, r in zip(names, ranges, strict=True)})
        return points

    if spec.mode == "sobol":
        try:
            from scipy.stats.qmc import Sobol  # type: ignore[import-untyped]
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError("sobol sampling requires scipy") from exc

        engine = Sobol(d=len(ranges), scramble=True, seed=seed)
        raw_samples = engine.random(spec.n_samples)
        points = []
        for raw in raw_samples:
            point: dict[str, float] = {}
            for idx, (name, bounds) in enumerate(zip(names, ranges, strict=True)):
                span = bounds.upper - bounds.lower
                point[name] = bounds.lower + (raw[idx] * span)
            points.append(point)
        return points

    raise ValueError(f"unsupported sweep mode: {spec.mode}")
