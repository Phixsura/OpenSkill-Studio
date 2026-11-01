"""Consumer API Idempotency Config — configure idempotency behavior per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class IdempotencyConfig:
    consumer_id: str
    ttl_seconds: int = 86400       # how long idempotency keys are stored
    max_key_length: int = 128       # max length of idempotency key
    required_methods: list[str] = field(default_factory=lambda: ["POST", "PUT", "PATCH"])
    enforce: bool = True            # if True, reject requests without keys for required methods
    key_header: str = "Idempotency-Key"

@dataclass
class IdempotencyCheckResult:
    required: bool
    provided: bool
    valid: bool
    reason: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiIdempotencyConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], IdempotencyConfig] = {}

    def set_config(self, installation_id: str, config: IdempotencyConfig) -> IdempotencyConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.ttl_seconds < 60:
            raise ValueError("ttl_seconds must be at least 60")
        if config.max_key_length < 16:
            raise ValueError("max_key_length must be at least 16")
        for m in config.required_methods:
            if m.upper() not in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                raise ValueError(f"Invalid method: {m}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def check(self, installation_id: str, consumer_id: str, method: str, idempotency_key: str | None) -> IdempotencyCheckResult:
        config = self._configs.get((installation_id, consumer_id))
        if not config:
            return IdempotencyCheckResult(required=False, provided=idempotency_key is not None, valid=True, reason="no_config")
        required = method.upper() in [m.upper() for m in config.required_methods]
        if not required:
            return IdempotencyCheckResult(required=False, provided=idempotency_key is not None, valid=True, reason="method_not_required")
        if idempotency_key is None:
            if config.enforce:
                return IdempotencyCheckResult(required=True, provided=False, valid=False, reason="key_missing")
            return IdempotencyCheckResult(required=True, provided=False, valid=True, reason="key_optional")
        if len(idempotency_key) > config.max_key_length:
            return IdempotencyCheckResult(required=True, provided=True, valid=False, reason="key_too_long")
        if len(idempotency_key) < 8:
            return IdempotencyCheckResult(required=True, provided=True, valid=False, reason="key_too_short")
        return IdempotencyCheckResult(required=True, provided=True, valid=True, reason="valid")

    def get_config(self, installation_id: str, consumer_id: str) -> IdempotencyConfig | None:
        return self._configs.get((installation_id, consumer_id))
