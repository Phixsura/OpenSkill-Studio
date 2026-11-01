"""App API Health Score — compute composite health scores.

Manages health scoring:
- Define health dimensions with weights
- Record dimension scores
- Compute weighted composite score
- Per-installation scoped scores
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class HealthDimension:
    """A health score dimension."""

    dimension_id: str
    name: str
    weight: float = 1.0
    score: float = 100.0  # 0-100


class AppAPIHealthScore:
    """Compute composite health scores."""

    def __init__(self) -> None:
        self._dimensions: dict[tuple[str, str], HealthDimension] = {}

    def add_dimension(
        self, installation_id: str, dimension_id: str, name: str,
        weight: float = 1.0,
    ) -> HealthDimension:
        if not installation_id:
            raise ValueError("installation_id is required")
        if weight <= 0:
            raise ValueError("weight must be positive")

        d = HealthDimension(dimension_id=dimension_id, name=name, weight=weight)
        self._dimensions[(installation_id, dimension_id)] = d
        return d

    def update_score(self, installation_id: str, dimension_id: str, score: float) -> HealthDimension:
        if not (0 <= score <= 100):
            raise ValueError("score must be between 0 and 100")
        d = self._get(installation_id, dimension_id)
        d.score = score
        return d

    def composite_score(self, installation_id: str) -> float:
        dims = self._list(installation_id)
        if not dims:
            return 100.0
        total_weight = sum(d.weight for d in dims)
        weighted_sum = sum(d.score * d.weight for d in dims)
        return round(weighted_sum / total_weight, 1)

    def list_dimensions(self, installation_id: str) -> list[HealthDimension]:
        return self._list(installation_id)

    def _list(self, installation_id: str) -> list[HealthDimension]:
        return [d for (inst, _), d in self._dimensions.items() if inst == installation_id]

    def _get(self, installation_id: str, dimension_id: str) -> HealthDimension:
        key = (installation_id, dimension_id)
        d = self._dimensions.get(key)
        if d is None:
            raise KeyError(f"Dimension {dimension_id} not found")
        return d
