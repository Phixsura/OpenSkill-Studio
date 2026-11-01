"""Consumer API Key Metadata — attach and query metadata on API keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class APIKeyMeta:
    key_id: str
    consumer_id: str
    label: str = ""
    environment: str = "production"  # "production", "staging", "development"
    created_at: datetime | None = None
    last_used_at: datetime | None = None
    request_count: int = 0
    tags: dict[str, str] = field(default_factory=dict)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyMetadata:
    def __init__(self) -> None:
        self._keys: dict[tuple[str, str, str], APIKeyMeta] = {}  # (inst, consumer, key_id)

    def set_metadata(self, installation_id: str, meta: APIKeyMeta) -> APIKeyMeta:
        if not installation_id:
            raise ValueError("installation_id is required")
        if meta.environment not in ("production", "staging", "development"):
            raise ValueError(f"Invalid environment: {meta.environment}")
        meta.created_at = meta.created_at or datetime.utcnow()
        self._keys[(installation_id, meta.consumer_id, meta.key_id)] = meta
        return meta

    def get(self, installation_id: str, consumer_id: str, key_id: str) -> APIKeyMeta | None:
        return self._keys.get((installation_id, consumer_id, key_id))

    def record_usage(self, installation_id: str, consumer_id: str, key_id: str, now: datetime) -> APIKeyMeta:
        key = (installation_id, consumer_id, key_id)
        meta = self._keys.get(key)
        if not meta:
            raise ValueError("Key not found")
        meta.last_used_at = now
        meta.request_count += 1
        return meta

    def list_keys(self, installation_id: str, consumer_id: str, environment: str | None = None) -> list[APIKeyMeta]:
        keys = [m for (inst, cid, _), m in self._keys.items() if inst == installation_id and cid == consumer_id]
        if environment:
            keys = [k for k in keys if k.environment == environment]
        return sorted(keys, key=lambda k: k.label)

    def find_by_tag(self, installation_id: str, consumer_id: str, tag_key: str, tag_value: str) -> list[APIKeyMeta]:
        return [m for (inst, cid, _), m in self._keys.items() if inst == installation_id and cid == consumer_id and m.tags.get(tag_key) == tag_value]
