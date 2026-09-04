"""Shared types for part calculators."""

from dataclasses import dataclass, field


@dataclass
class LineResult:
    unit_cost: float
    extra: dict = field(default_factory=dict)


class LookupMissError(Exception):
    """Raised when no matching row is found in the loaded chart."""
