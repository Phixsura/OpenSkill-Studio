"""API Consumer Response Envelope — standardize API response format per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class EnvelopeConfig:
    consumer_id: str
    wrap_key: str = "data"  # key to wrap response data
    include_meta: bool = True
    include_request_id: bool = True
    include_timestamp: bool = True
    include_pagination: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiResponseEnvelope:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], EnvelopeConfig] = {}

    def configure(self, installation_id: str, config: EnvelopeConfig) -> EnvelopeConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if not config.wrap_key: raise ValueError("wrap_key is required")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def wrap(self, installation_id: str, consumer_id: str, data: object, request_id: str = "", total: int | None = None, page: int | None = None) -> dict:
        config = self._configs.get((installation_id, consumer_id))
        if config is None:
            return {"data": data}
        result: dict[str, object] = {config.wrap_key: data}
        if config.include_meta:
            meta: dict[str, object] = {}
            if config.include_request_id and request_id: meta["request_id"] = request_id
            if config.include_timestamp: meta["timestamp"] = int(time.time())
            if config.include_pagination and total is not None:
                meta["total"] = total
                if page is not None: meta["page"] = page
            if meta: result["meta"] = meta
        return result

    def get_config(self, installation_id: str, consumer_id: str) -> EnvelopeConfig | None:
        return self._configs.get((installation_id, consumer_id))

    def list_configs(self, installation_id: str) -> list[EnvelopeConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
