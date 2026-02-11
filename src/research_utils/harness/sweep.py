"""Sampling utilities for deterministic sweep generation."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import random
from typing import Mapping, Sequence


SamplePoint = dict[str, float]
SamplingMode = str


@dataclass(frozen=True)
class SweepSpec:
    """Sweep definition supporting grid, random, and Sobol modes."""

    parameters: Mapping[str, Sequence[float]]
    mode: SamplingMode = "grid"
    num_samples: int | None = None
    candidates: tuple[SamplePoint, ...] = ()

    def sample(self, seed: int) -> tuple[SamplePoint, ...]:
        """Return deterministic sample points in stable order."""
        if self.candidates:
            return tuple(dict(candidate) for candidate in self.candidates)

        mode = self.mode.lower()
        if mode == "grid":
            return _sample_grid(self.parameters)
        if mode == "random":
            return _sample_random(self.parameters, seed=seed, num_samples=self.num_samples)
        if mode == "sobol":
            return _sample_sobol(self.parameters, seed=seed, num_samples=self.num_samples)
        msg = f"unsupported sampling mode: {self.mode}"
        raise ValueError(msg)


def _stable_parameter_names(parameters: Mapping[str, Sequence[float]]) -> tuple[str, ...]:
    return tuple(sorted(parameters.keys()))


def _sample_grid(parameters: Mapping[str, Sequence[float]]) -> tuple[SamplePoint, ...]:
    names = _stable_parameter_names(parameters)
    values = [tuple(float(v) for v in parameters[name]) for name in names]

    points: list[SamplePoint] = []
    for row in product(*values):
        points.append({name: value for name, value in zip(names, row, strict=True)})
    return tuple(points)


def _bounds(values: Sequence[float]) -> tuple[float, float]:
    if len(values) < 2:
        msg = "random/sobol sampling requires at least two values per parameter"
        raise ValueError(msg)
    low = float(min(values))
    high = float(max(values))
    if low == high:
        msg = "sampling bounds must have non-zero width"
        raise ValueError(msg)
    return (low, high)


def _resolve_num_samples(num_samples: int | None) -> int:
    if num_samples is None:
        msg = "num_samples is required for random or sobol sampling"
        raise ValueError(msg)
    if num_samples <= 0:
        msg = "num_samples must be positive"
        raise ValueError(msg)
    return num_samples


def _sample_random(
    parameters: Mapping[str, Sequence[float]], *, seed: int, num_samples: int | None
) -> tuple[SamplePoint, ...]:
    names = _stable_parameter_names(parameters)
    ranges = [_bounds(parameters[name]) for name in names]
    n = _resolve_num_samples(num_samples)
    rng = random.Random(seed)

    points: list[SamplePoint] = []
    for _ in range(n):
        point: SamplePoint = {}
        for name, (low, high) in zip(names, ranges, strict=True):
            point[name] = rng.uniform(low, high)
        points.append(point)
    return tuple(points)


def _sample_sobol(
    parameters: Mapping[str, Sequence[float]], *, seed: int, num_samples: int | None
) -> tuple[SamplePoint, ...]:
    try:
        from scipy.stats import qmc  # type: ignore[import-untyped]
    except ImportError as exc:  # pragma: no cover - optional dependency path
        msg = "sobol sampling requires scipy"
        raise RuntimeError(msg) from exc

    names = _stable_parameter_names(parameters)
    ranges = [_bounds(parameters[name]) for name in names]
    n = _resolve_num_samples(num_samples)

    sampler = qmc.Sobol(d=len(names), scramble=True, seed=seed)
    unit_samples = sampler.random(n=n)

    points: list[SamplePoint] = []
    for row in unit_samples:
        point: SamplePoint = {}
        for index, name in enumerate(names):
            low, high = ranges[index]
            point[name] = low + float(row[index]) * (high - low)
        points.append(point)
    return tuple(points)


__all__ = ["SamplingMode", "SweepSpec"]
