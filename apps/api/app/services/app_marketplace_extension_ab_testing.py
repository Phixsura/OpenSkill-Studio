"""A/B Testing — run experiments on extension features and configurations.

Allows developers to split users into groups and measure the impact
of different extension configurations or feature variants.
"""
from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Variant:
    name: str
    weight: int  # percentage 0-100
    config: dict = field(default_factory=dict)
    conversions: int = 0
    impressions: int = 0

    @property
    def conversion_rate(self) -> float:
        return round(self.conversions / max(1, self.impressions) * 100, 2)


@dataclass
class Experiment:
    experiment_id: str
    extension_id: str
    name: str
    variants: list[Variant]
    status: ExperimentStatus = ExperimentStatus.DRAFT
    created_at: str = ""
    started_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class ABTestingService:
    """Manages A/B testing experiments for extensions."""

    def __init__(self):
        self._experiments: dict[str, Experiment] = {}

    def create_experiment(self, experiment_id: str, extension_id: str, name: str,
                          variants: list[dict]) -> tuple[Experiment | None, str]:
        """Create experiment. Variants: [{name, weight, config}]. Weights must sum to 100."""
        total_weight = sum(v.get("weight", 0) for v in variants)
        if total_weight != 100:
            return None, f"Variant weights must sum to 100, got {total_weight}"
        if len(variants) < 2:
            return None, "Need at least 2 variants"

        parsed = [Variant(name=v["name"], weight=v["weight"],
                          config=v.get("config", {})) for v in variants]
        exp = Experiment(experiment_id=experiment_id, extension_id=extension_id,
                         name=name, variants=parsed)
        self._experiments[experiment_id] = exp
        return exp, "Created"

    def start(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if exp and exp.status in (ExperimentStatus.DRAFT, ExperimentStatus.PAUSED):
            exp.status = ExperimentStatus.RUNNING
            exp.started_at = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def pause(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if exp and exp.status == ExperimentStatus.RUNNING:
            exp.status = ExperimentStatus.PAUSED
            return True
        return False

    def complete(self, experiment_id: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if exp and exp.status == ExperimentStatus.RUNNING:
            exp.status = ExperimentStatus.COMPLETED
            return True
        return False

    def assign_variant(self, experiment_id: str, user_id: str) -> str | None:
        """Deterministically assign a user to a variant."""
        exp = self._experiments.get(experiment_id)
        if not exp or exp.status != ExperimentStatus.RUNNING:
            return None

        hash_val = int(hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest(), 16)
        bucket = hash_val % 100
        cumulative = 0
        for variant in exp.variants:
            cumulative += variant.weight
            if bucket < cumulative:
                variant.impressions += 1
                return variant.name
        return exp.variants[-1].name

    def record_conversion(self, experiment_id: str, variant_name: str) -> bool:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return False
        for v in exp.variants:
            if v.name == variant_name:
                v.conversions += 1
                return True
        return False

    def get_results(self, experiment_id: str) -> dict | None:
        exp = self._experiments.get(experiment_id)
        if not exp:
            return None
        variants_data = [{
            "name": v.name, "weight": v.weight,
            "impressions": v.impressions, "conversions": v.conversions,
            "conversion_rate": v.conversion_rate,
        } for v in exp.variants]
        winner = max(exp.variants, key=lambda v: v.conversion_rate) if exp.variants else None
        return {
            "experiment_id": experiment_id, "status": exp.status.value,
            "variants": variants_data,
            "winner": winner.name if winner and winner.impressions > 0 else None,
        }
