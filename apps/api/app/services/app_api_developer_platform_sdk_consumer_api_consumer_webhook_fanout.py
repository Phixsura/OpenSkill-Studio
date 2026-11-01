"""Consumer API Webhook Fanout — deliver events to multiple webhook endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class FanoutTarget:
    target_id: str
    webhook_url: str
    active: bool = True
    filter_events: list[str] = field(default_factory=list)  # empty = all events

@dataclass
class FanoutConfig:
    consumer_id: str
    targets: list[FanoutTarget] = field(default_factory=list)
    max_targets: int = 10

@dataclass
class FanoutResult:
    event_type: str
    targets_matched: int
    targets_skipped: int
    deliveries: list[str]  # target IDs that received

class AppAPIDeveloperPlatformSDKConsumerApiConsumerWebhookFanout:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], FanoutConfig] = {}

    def configure(self, installation_id: str, config: FanoutConfig) -> FanoutConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if len(config.targets) > config.max_targets:
            raise ValueError(f"Exceeds max targets ({config.max_targets})")
        for t in config.targets:
            if not t.webhook_url.startswith("https://"):
                raise ValueError(f"Target {t.target_id} must use HTTPS")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def add_target(self, installation_id: str, consumer_id: str, target: FanoutTarget) -> FanoutConfig:
        key = (installation_id, consumer_id)
        config = self._configs.get(key)
        if not config:
            config = FanoutConfig(consumer_id=consumer_id)
            self._configs[key] = config
        if not target.webhook_url.startswith("https://"):
            raise ValueError("webhook_url must use HTTPS")
        if len(config.targets) >= config.max_targets:
            raise ValueError("Max targets reached")
        if any(t.target_id == target.target_id for t in config.targets):
            raise ValueError(f"Target {target.target_id} already exists")
        config.targets.append(target)
        return config

    def remove_target(self, installation_id: str, consumer_id: str, target_id: str) -> None:
        config = self._configs.get((installation_id, consumer_id))
        if not config:
            raise ValueError("Config not found")
        before = len(config.targets)
        config.targets = [t for t in config.targets if t.target_id != target_id]
        if len(config.targets) == before:
            raise ValueError("Target not found")

    def fanout(self, installation_id: str, consumer_id: str, event_type: str) -> FanoutResult:
        config = self._configs.get((installation_id, consumer_id))
        if not config:
            return FanoutResult(event_type=event_type, targets_matched=0, targets_skipped=0, deliveries=[])
        matched: list[str] = []
        skipped = 0
        for t in config.targets:
            if not t.active:
                skipped += 1
                continue
            if t.filter_events and event_type not in t.filter_events:
                skipped += 1
                continue
            matched.append(t.target_id)
        return FanoutResult(event_type=event_type, targets_matched=len(matched), targets_skipped=skipped, deliveries=matched)

    def get_config(self, installation_id: str, consumer_id: str) -> FanoutConfig | None:
        return self._configs.get((installation_id, consumer_id))
