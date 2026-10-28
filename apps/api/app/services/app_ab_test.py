"""App A/B Test Manager — experiment assignment and result tracking.

Manages A/B test experiments for installed apps:
- Create experiments with named variants
- Deterministic user assignment via hashing
- Track conversions per variant
- Compute conversion rates and statistical summary
- Per-installation scoped experiments
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Variant:
    """An experiment variant."""

    name: str
    weight: float = 1.0  # relative weight for assignment
    exposures: int = 0
    conversions: int = 0

    @property
    def conversion_rate(self) -> float:
        return (self.conversions / self.exposures * 100) if self.exposures > 0 else 0.0


@dataclass
class Experiment:
    """An A/B test experiment."""

    experiment_id: str
    installation_id: str
    name: str
    variants: list[Variant] = field(default_factory=list)
    active: bool = True


@dataclass
class Assignment:
    """User's assigned variant."""

    user_id: str
    experiment_id: str
    variant_name: str


class AppABTestManager:
    """Manage A/B test experiments for installed apps."""

    def __init__(self) -> None:
        # (installation_id, experiment_id) → Experiment
        self._experiments: dict[tuple[str, str], Experiment] = {}
        # (installation_id, experiment_id, user_id) → variant_name
        self._assignments: dict[tuple[str, str, str], str] = {}

    def create_experiment(
        self,
        installation_id: str,
        experiment_id: str,
        name: str,
        variants: list[dict],
    ) -> Experiment:
        """Create a new experiment. variants: [{"name": "control", "weight": 1.0}, ...]"""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not experiment_id:
            raise ValueError("experiment_id is required")
        if len(variants) < 2:
            raise ValueError("At least 2 variants required")

        key = (installation_id, experiment_id)
        if key in self._experiments:
            raise ValueError(f"Experiment {experiment_id} already exists")

        variant_objs = [
            Variant(name=v["name"], weight=v.get("weight", 1.0))
            for v in variants
        ]
        exp = Experiment(
            experiment_id=experiment_id,
            installation_id=installation_id,
            name=name,
            variants=variant_objs,
        )
        self._experiments[key] = exp
        return exp

    def assign(
        self, installation_id: str, experiment_id: str, user_id: str
    ) -> Assignment:
        """Assign a user to a variant (deterministic, sticky)."""
        exp = self._get(installation_id, experiment_id)
        if not exp.active:
            raise ValueError("Experiment is not active")

        assign_key = (installation_id, experiment_id, user_id)
        existing = self._assignments.get(assign_key)
        if existing:
            return Assignment(user_id=user_id, experiment_id=experiment_id, variant_name=existing)

        # Deterministic assignment
        variant = self._pick_variant(experiment_id, user_id, exp.variants)
        self._assignments[assign_key] = variant.name
        variant.exposures += 1

        return Assignment(user_id=user_id, experiment_id=experiment_id, variant_name=variant.name)

    def record_conversion(
        self, installation_id: str, experiment_id: str, user_id: str
    ) -> bool:
        """Record a conversion for a user's assigned variant. Returns False if not assigned."""
        exp = self._get(installation_id, experiment_id)
        assign_key = (installation_id, experiment_id, user_id)
        variant_name = self._assignments.get(assign_key)
        if variant_name is None:
            return False

        for v in exp.variants:
            if v.name == variant_name:
                v.conversions += 1
                return True
        return False

    def get_results(self, installation_id: str, experiment_id: str) -> dict:
        """Get experiment results."""
        exp = self._get(installation_id, experiment_id)
        return {
            "experiment_id": exp.experiment_id,
            "name": exp.name,
            "active": exp.active,
            "variants": [
                {
                    "name": v.name,
                    "exposures": v.exposures,
                    "conversions": v.conversions,
                    "conversion_rate": round(v.conversion_rate, 2),
                }
                for v in exp.variants
            ],
        }

    def stop_experiment(self, installation_id: str, experiment_id: str) -> Experiment:
        exp = self._get(installation_id, experiment_id)
        exp.active = False
        return exp

    def list_experiments(self, installation_id: str) -> list[Experiment]:
        return [
            exp for (inst, _), exp in self._experiments.items()
            if inst == installation_id
        ]

    def _pick_variant(self, experiment_id: str, user_id: str, variants: list[Variant]) -> Variant:
        h = hashlib.sha256(f"{experiment_id}:{user_id}".encode()).hexdigest()
        bucket = int(h[:8], 16) % 10000
        total_weight = sum(v.weight for v in variants)
        cumulative = 0.0
        for v in variants:
            cumulative += (v.weight / total_weight) * 10000
            if bucket < cumulative:
                return v
        return variants[-1]

    def _get(self, installation_id: str, experiment_id: str) -> Experiment:
        key = (installation_id, experiment_id)
        exp = self._experiments.get(key)
        if exp is None:
            raise KeyError(f"Experiment {experiment_id} not found")
        return exp
