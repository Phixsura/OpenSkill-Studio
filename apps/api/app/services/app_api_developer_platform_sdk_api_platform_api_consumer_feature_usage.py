"""App API Developer Consumer Feature Usage — track which features each consumer uses."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerFeatureUsage:
    consumer_id: str
    features_used: dict[str, int] = field(default_factory=dict)  # feature -> usage count

    @property
    def feature_count(self) -> int:
        return len(self.features_used)

    @property
    def total_usage(self) -> int:
        return sum(self.features_used.values())

    @property
    def top_feature(self) -> str:
        if not self.features_used: return ""
        return max(self.features_used, key=self.features_used.get)

class AppAPIDeveloperPlatformSDKApiPlatformApiConsumerFeatureUsage:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], ConsumerFeatureUsage] = {}

    def track(self, installation_id: str, consumer_id: str, feature: str, count: int = 1) -> ConsumerFeatureUsage:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._usage:
            self._usage[key] = ConsumerFeatureUsage(consumer_id=consumer_id)
        u = self._usage[key]
        u.features_used[feature] = u.features_used.get(feature, 0) + count
        return u

    def feature_popularity(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), u in self._usage.items():
            if inst == installation_id:
                for f in u.features_used: counts[f] = counts.get(f, 0) + 1
        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def low_adoption_features(self, installation_id: str, min_users: int = 5) -> list[str]:
        pop = self.feature_popularity(installation_id)
        return [f for f, c in pop.items() if c < min_users]

    def all_usage(self, installation_id: str) -> list[ConsumerFeatureUsage]:
        return [u for (inst, _), u in self._usage.items() if inst == installation_id]
