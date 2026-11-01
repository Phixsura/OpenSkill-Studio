"""API Consumer Request ID Generator — generate unique request IDs with configurable formats."""
from __future__ import annotations
from dataclasses import dataclass
import secrets
import time
import structlog

log = structlog.get_logger()

@dataclass
class RequestIdConfig:
    prefix: str = "req"
    format: str = "hex"  # "hex", "uuid", "ulid_like"
    length: int = 24
    include_timestamp: bool = False

VALID_FORMATS = {"hex", "uuid", "ulid_like"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestIdGenerator:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], RequestIdConfig] = {}
        self._generated: dict[str, int] = {}

    def configure(self, installation_id: str, consumer_id: str, config: RequestIdConfig) -> RequestIdConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.format not in VALID_FORMATS: raise ValueError(f"Invalid format: {config.format}")
        if config.length < 8 or config.length > 64: raise ValueError("length must be 8-64")
        self._configs[(installation_id, consumer_id)] = config
        return config

    def generate(self, installation_id: str, consumer_id: str = "") -> str:
        config = self._configs.get((installation_id, consumer_id))
        if config is None:
            config = RequestIdConfig()
        if config.format == "uuid":
            import uuid
            rid = f"{config.prefix}-{uuid.uuid4()}"
        elif config.format == "ulid_like":
            ts = hex(int(time.time() * 1000))[2:]
            rand = secrets.token_hex((config.length - len(ts)) // 2)
            rid = f"{config.prefix}-{ts}{rand}"
        else:
            rid = f"{config.prefix}-{secrets.token_hex(config.length // 2)}"
        if config.include_timestamp:
            rid = f"{rid}-{int(time.time())}"
        self._generated[installation_id] = self._generated.get(installation_id, 0) + 1
        return rid

    def total_generated(self, installation_id: str) -> int:
        return self._generated.get(installation_id, 0)

    def get_config(self, installation_id: str, consumer_id: str) -> RequestIdConfig | None:
        return self._configs.get((installation_id, consumer_id))
