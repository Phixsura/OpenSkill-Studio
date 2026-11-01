"""Consumer API Content Negotiation — manage response formats per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

SUPPORTED_FORMATS = {"application/json", "application/xml", "text/csv", "application/yaml"}

@dataclass
class NegotiationConfig:
    consumer_id: str
    supported_formats: list[str] = field(default_factory=lambda: ["application/json"])
    default_format: str = "application/json"
    strict: bool = False  # if True, reject unsupported Accept headers

@dataclass
class NegotiationResult:
    content_type: str
    negotiated: bool  # True if matched Accept header, False if fell back to default
    quality: float = 1.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiContentNegotiation:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], NegotiationConfig] = {}

    def set_config(self, installation_id: str, config: NegotiationConfig) -> NegotiationConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.default_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {config.default_format}")
        for f in config.supported_formats:
            if f not in SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {f}")
        if config.default_format not in config.supported_formats:
            raise ValueError("default_format must be in supported_formats")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def negotiate(self, installation_id: str, consumer_id: str, accept_header: str) -> NegotiationResult:
        config = self._configs.get((installation_id, consumer_id), NegotiationConfig(consumer_id=consumer_id))
        if not accept_header or accept_header == "*/*":
            return NegotiationResult(content_type=config.default_format, negotiated=False)
        # Parse Accept header (simplified: comma-separated, ignore q-values)
        accepted = [a.strip().split(";")[0].strip() for a in accept_header.split(",")]
        for a in accepted:
            if a in config.supported_formats:
                return NegotiationResult(content_type=a, negotiated=True)
        # No match
        if config.strict:
            raise ValueError(f"No acceptable format. Supported: {', '.join(config.supported_formats)}")
        return NegotiationResult(content_type=config.default_format, negotiated=False)

    def get_config(self, installation_id: str, consumer_id: str) -> NegotiationConfig | None:
        return self._configs.get((installation_id, consumer_id))
