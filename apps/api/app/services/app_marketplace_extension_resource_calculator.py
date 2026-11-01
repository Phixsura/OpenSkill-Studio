"""Resource Calculator — estimate resource needs for extension deployment.

Calculates CPU, memory, storage, bandwidth requirements based on
expected traffic, features used, and provides tier recommendations.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class RecommendedTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class ResourceEstimate:
    cpu_cores: float
    memory_mb: int
    storage_mb: int
    bandwidth_gb: float
    estimated_cost_cents: int
    recommended_tier: RecommendedTier


class ExtensionResourceCalculatorService:
    """Estimates resource requirements for extensions."""

    TIER_THRESHOLDS = {
        RecommendedTier.FREE: {"cpu": 0.5, "memory": 256, "bandwidth": 1},
        RecommendedTier.STARTER: {"cpu": 1.0, "memory": 512, "bandwidth": 10},
        RecommendedTier.PRO: {"cpu": 2.0, "memory": 2048, "bandwidth": 100},
        RecommendedTier.ENTERPRISE: {"cpu": 8.0, "memory": 8192, "bandwidth": 1000},
    }

    def estimate(self, expected_users: int, features: list[str],
                 has_database: bool = False, has_file_storage: bool = False,
                 api_calls_per_day: int = 0) -> ResourceEstimate:
        # Base resources
        cpu = 0.1 + expected_users * 0.001
        memory = 128 + expected_users * 0.5
        storage = 100  # base MB
        bandwidth = expected_users * 0.01  # GB

        # Feature multipliers
        if has_database:
            memory += 256
            storage += 500
            cpu += 0.2
        if has_file_storage:
            storage += 2000
            bandwidth *= 2
        if "realtime" in features:
            cpu *= 1.5
            memory *= 1.3
        if "ml_inference" in features:
            cpu *= 3
            memory *= 2
        if "video_processing" in features:
            cpu *= 4
            memory *= 3
            bandwidth *= 5

        # API overhead
        cpu += api_calls_per_day * 0.0001
        bandwidth += api_calls_per_day * 0.00001

        cpu = round(cpu, 2)
        memory = int(memory)
        storage = int(storage)
        bandwidth = round(bandwidth, 2)

        # Cost estimate (simplified)
        cost = int(cpu * 1000 + memory * 0.5 + storage * 0.1 + bandwidth * 100)

        # Recommend tier
        tier = RecommendedTier.FREE
        for t, limits in self.TIER_THRESHOLDS.items():
            if cpu <= limits["cpu"] and memory <= limits["memory"] and bandwidth <= limits["bandwidth"]:
                tier = t
                break
        else:
            tier = RecommendedTier.ENTERPRISE

        return ResourceEstimate(
            cpu_cores=cpu, memory_mb=memory, storage_mb=storage,
            bandwidth_gb=bandwidth, estimated_cost_cents=cost,
            recommended_tier=tier,
        )
