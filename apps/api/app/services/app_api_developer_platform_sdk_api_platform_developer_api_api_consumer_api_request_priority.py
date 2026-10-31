"""API Consumer Request Priority — prioritize API requests by consumer tier."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PriorityConfig:
    consumer_id: str
    priority_level: int  # 1 (lowest) to 10 (highest)
    queue_position: str = "normal"  # "normal", "high", "critical"
    max_concurrent: int = 10

VALID_POSITIONS = {"normal", "high", "critical"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestPriority:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], PriorityConfig] = {}

    def set_priority(self, installation_id: str, config: PriorityConfig) -> PriorityConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not 1 <= config.priority_level <= 10: raise ValueError("priority must be 1-10")
        if config.queue_position not in VALID_POSITIONS: raise ValueError(f"Invalid position: {config.queue_position}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def get_priority(self, installation_id: str, consumer_id: str) -> int:
        config = self._configs.get((installation_id, consumer_id))
        return config.priority_level if config else 5  # default middle priority

    def should_preempt(self, installation_id: str, consumer_id: str) -> bool:
        config = self._configs.get((installation_id, consumer_id))
        return config is not None and config.queue_position == "critical"

    def sorted_consumers(self, installation_id: str) -> list[PriorityConfig]:
        configs = [c for (inst, _), c in self._configs.items() if inst == installation_id]
        return sorted(configs, key=lambda c: -c.priority_level)

    def list_configs(self, installation_id: str) -> list[PriorityConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
