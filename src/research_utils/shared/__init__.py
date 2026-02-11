"""Shared utility exports."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Seed:
    """Simple explicit seed wrapper."""

    value: int


__all__ = ["Seed"]
