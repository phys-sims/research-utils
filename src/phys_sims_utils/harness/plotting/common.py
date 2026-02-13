"""Shared plotting utilities for deterministic harness visualizations."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any


def require_matplotlib() -> Any:
    """Import and return ``matplotlib.pyplot`` or raise a clear error."""
    try:
        return import_module("matplotlib.pyplot")
    except ImportError as exc:  # pragma: no cover - optional dependency path
        msg = "plotting helpers require matplotlib"
        raise RuntimeError(msg) from exc


def make_output_path(path: str | Path, *, default_suffix: str = ".png") -> Path:
    """Create parent directories and ensure output path has a file suffix."""
    output = Path(path)
    if output.suffix == "":
        output = output.with_suffix(default_suffix)
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def create_figure(*, figsize: tuple[float, float] = (7.0, 4.5)) -> tuple[Any, Any]:
    """Create a canonical figure and axes with a deterministic style."""
    plt = require_matplotlib()
    fig, ax = plt.subplots(figsize=figsize, constrained_layout=True)
    return fig, ax


def finalize_figure(
    fig: Any,
    output_path: str | Path,
    *,
    dpi: int = 150,
    close: bool = True,
) -> Path:
    """Save a figure to disk and optionally close it."""
    destination = make_output_path(output_path)
    fig.savefig(destination, dpi=dpi)

    if close:
        plt = require_matplotlib()
        plt.close(fig)

    return destination


__all__ = [
    "create_figure",
    "finalize_figure",
    "make_output_path",
    "require_matplotlib",
]
