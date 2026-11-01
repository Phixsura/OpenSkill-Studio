"""App A/B Test — manage A/B test experiments.

Manages A/B testing:
- Define experiments with variants and weights
- Deterministic assignment by user ID
- Track variant impressions and conversions
- Per-installation scoped experiments
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Variant:
    """A test variant."""

    name: str
    weight: float = 1.0
    impressions: int = 0
    conversions: int = 0

    @property
    def conversion_rate(self) -> float:
        if self.impressions == 0:
            return 0.0
        return round(self.conversions / self.impressions * 100, 1)


@dataclass
class Experiment:
    """An A/B test experiment."""

    experiment_id: str
    name: str
    variants: list[Variant]
    active: bool = True


class AppABTest:
    """Manage A/B test experiments."""

    def __init__(self) -> None:
        self._experiments: dict[tuple[str, str], Experiment] = {}

    def create(
        self, installation_id: str, experiment_id: str, name: str,
        variants: list[dict],
    ) -> Experiment:
        if not installation_id:
            raise ValueError("installation_id is required")
        if len(variants) < 2:
            raise ValueError("at least 2 variants required")

        variant_objs = [
            Variant(name=v["name"], weight=v.get("weight", 1.0))
            for v in variants
        ]

        # Validate positive weights
        if any(v.weight <= 0 for v in variant_objs):
            raise ValueError("weights must be positive")

        exp = Experiment(
            experiment_id=experiment_id, name=name, variants=variant_objs,
        )
        self._experiments[(installation_id, experiment_id)] = exp
        return exp

    def assign(self, installation_id: str, experiment_id: str, user_id: str) -> str:
        """Deterministically assign a user to a variant."""
        exp = self._get(installation_id, experiment_id)
        if not exp.active:
            raise ValueError("Experiment is not active")

        # Deterministic hash-based assignment
        h = int(hashlib.sha256(f"{experiment_id}:{user_id}".encode()).hexdigest()[:8], 16)
        total_weight = sum(v.weight for v in exp.variants)
        threshold = (h % 10000) / 10000 * total_weight

        cumulative = 0.0
        for v in exp.variants:
            cumulative += v.weight
            if threshold < cumulative:
                v.impressions += 1
                return v.name

        # Fallback to last variant
        exp.variants[-1].impressions += 1
        return exp.variants[-1].name

    def convert(self, installation_id: str, experiment_id: str, variant_name: str) -> Variant:
        exp = self._get(installation_id, experiment_id)
        for v in exp.variants:
            if v.name == variant_name:
                v.conversions += 1
                return v
        raise KeyError(f"Variant {variant_name} not found")

    def results(self, installation_id: str, experiment_id: str) -> list[dict]:
        exp = self._get(installation_id, experiment_id)
        return [
            {"name": v.name, "impressions": v.impressions,
             "conversions": v.conversions, "rate": v.conversion_rate}
            for v in exp.variants
        ]

    def deactivate(self, installation_id: str, experiment_id: str) -> Experiment:
        exp = self._get(installation_id, experiment_id)
        exp.active = False
        return exp

    def list_experiments(self, installation_id: str) -> list[Experiment]:
        return [e for (inst, _), e in self._experiments.items() if inst == installation_id]

    def _get(self, installation_id: str, experiment_id: str) -> Experiment:
        key = (installation_id, experiment_id)
        e = self._experiments.get(key)
        if e is None:
            raise KeyError(f"Experiment {experiment_id} not found")
        return e
