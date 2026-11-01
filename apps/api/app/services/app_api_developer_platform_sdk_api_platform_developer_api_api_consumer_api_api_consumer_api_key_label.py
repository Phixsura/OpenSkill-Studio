"""API Consumer API Key Label — label and organize API keys with metadata."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class KeyLabel:
    key_id: str
    consumer_id: str
    label: str
    environment: str = "production"  # "production", "staging", "development", "test"
    tags: list[str] = field(default_factory=list)
    description: str = ""

VALID_ENVIRONMENTS = {"production", "staging", "development", "test"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiKeyLabel:
    def __init__(self) -> None:
        self._labels: dict[tuple[str, str], KeyLabel] = {}

    def set_label(self, installation_id: str, label: KeyLabel) -> KeyLabel:
        if not installation_id: raise ValueError("installation_id is required")
        if label.environment not in VALID_ENVIRONMENTS: raise ValueError(f"Invalid environment: {label.environment}")
        if not label.label: raise ValueError("label is required")
        self._labels[(installation_id, label.key_id)] = label
        return label

    def get_label(self, installation_id: str, key_id: str) -> KeyLabel | None:
        return self._labels.get((installation_id, key_id))

    def by_environment(self, installation_id: str, environment: str) -> list[KeyLabel]:
        return [l for (inst, _), l in self._labels.items() if inst == installation_id and l.environment == environment]

    def by_tag(self, installation_id: str, tag: str) -> list[KeyLabel]:
        return [l for (inst, _), l in self._labels.items() if inst == installation_id and tag in l.tags]

    def search(self, installation_id: str, query: str) -> list[KeyLabel]:
        q = query.lower()
        return [l for (inst, _), l in self._labels.items() if inst == installation_id and (q in l.label.lower() or q in l.description.lower())]

    def list_labels(self, installation_id: str) -> list[KeyLabel]:
        return [l for (inst, _), l in self._labels.items() if inst == installation_id]
