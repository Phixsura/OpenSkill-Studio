"""App API Developer Webhook Consumer Preference Manager — per-consumer delivery settings."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerDeliveryPreference:
    consumer_id: str
    max_retries: int = 3
    retry_delay_seconds: int = 30
    timeout_ms: int = 5000
    content_type: str = "application/json"
    signature_algorithm: str = "sha256"
    batch_enabled: bool = False

class AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager:
    def __init__(self) -> None:
        self._prefs: dict[tuple[str, str], ConsumerDeliveryPreference] = {}

    def set(self, installation_id: str, consumer_id: str, **kwargs) -> ConsumerDeliveryPreference:
        if not installation_id: raise ValueError("installation_id is required")
        p = ConsumerDeliveryPreference(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(p, k): setattr(p, k, v)
        if p.max_retries < 0: raise ValueError("max_retries must be >= 0")
        if p.timeout_ms < 100: raise ValueError("timeout must be >= 100ms")
        if p.signature_algorithm not in ("sha256", "sha512", "none"): raise ValueError("invalid algorithm")
        self._prefs[(installation_id, consumer_id)] = p
        return p

    def get(self, installation_id: str, consumer_id: str) -> ConsumerDeliveryPreference:
        return self._prefs.get((installation_id, consumer_id), ConsumerDeliveryPreference(consumer_id=consumer_id))

    def with_batch(self, installation_id: str) -> list[ConsumerDeliveryPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id and p.batch_enabled]

    def all_preferences(self, installation_id: str) -> list[ConsumerDeliveryPreference]:
        return [p for (inst, _), p in self._prefs.items() if inst == installation_id]
