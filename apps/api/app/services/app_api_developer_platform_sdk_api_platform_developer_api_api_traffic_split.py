"""API Traffic Split — route traffic between API versions with weighted splits."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class TrafficTarget:
    version: str
    weight: int  # 0-100
    upstream: str

@dataclass
class SplitConfig:
    split_id: str
    endpoint: str
    targets: list[TrafficTarget] = field(default_factory=list)
    sticky: bool = True  # use consumer_id for consistent routing

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiTrafficSplit:
    def __init__(self) -> None:
        self._splits: dict[tuple[str, str], SplitConfig] = {}

    def create_split(self, installation_id: str, split: SplitConfig) -> SplitConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not split.targets: raise ValueError("At least one target required")
        total_weight = sum(t.weight for t in split.targets)
        if total_weight != 100: raise ValueError(f"Weights must sum to 100, got {total_weight}")
        for t in split.targets:
            if t.weight < 0: raise ValueError("Weight must be non-negative")
        key = (installation_id, split.endpoint)
        self._splits[key] = split
        return split

    def resolve(self, installation_id: str, endpoint: str, consumer_id: str = "") -> TrafficTarget | None:
        split = self._splits.get((installation_id, endpoint))
        if split is None: return None
        if split.sticky and consumer_id:
            h = int(hashlib.sha256(consumer_id.encode()).hexdigest()[:8], 16)
            bucket = h % 100
        else:
            import random
            bucket = random.randint(0, 99)
        cumulative = 0
        for t in split.targets:
            cumulative += t.weight
            if bucket < cumulative: return t
        return split.targets[-1]

    def update_weights(self, installation_id: str, endpoint: str, weights: dict[str, int]) -> SplitConfig:
        split = self._splits.get((installation_id, endpoint))
        if split is None: raise KeyError(f"No split for {endpoint}")
        total = sum(weights.values())
        if total != 100: raise ValueError(f"Weights must sum to 100, got {total}")
        for t in split.targets:
            if t.version in weights: t.weight = weights[t.version]
        return split

    def list_splits(self, installation_id: str) -> list[SplitConfig]:
        return [s for (inst, _), s in self._splits.items() if inst == installation_id]

    def remove_split(self, installation_id: str, endpoint: str) -> bool:
        key = (installation_id, endpoint)
        if key in self._splits: del self._splits[key]; return True
        return False
