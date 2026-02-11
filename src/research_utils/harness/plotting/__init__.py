"""Plotting helpers for harness outputs."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportSpec:
    """Placeholder plotting/reporting spec."""

    title: str = "report"


__all__ = ["ReportSpec"]
