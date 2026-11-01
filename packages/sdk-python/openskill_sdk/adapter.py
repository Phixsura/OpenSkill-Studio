"""Provider Adapter and Ecosystem Source SDK base classes.

Third-party developers extend these to build custom adapters.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Capability:
    """Declares one capability an adapter provides."""

    key: str
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    pricing: dict = field(default_factory=dict)


@dataclass
class HealthCheck:
    """Result of a health check."""

    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: int = 0
    message: str | None = None
    checked_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class SourceRecord:
    """A single record from an external data source."""

    external_id: str
    data: dict
    source_type: str
    fetched_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    checksum: str = ""

    def __post_init__(self) -> None:
        if not self.checksum:
            self.checksum = hashlib.sha256(
                json.dumps(self.data, sort_keys=True).encode()
            ).hexdigest()[:16]


class ProviderAdapter(ABC):
    """Base class for third-party provider adapters.

    Example::

        class MyVideoAdapter(ProviderAdapter):
            name = "my-video"
            display_name = "My Video Generator"
            capabilities = [
                Capability(key="text_to_video", pricing={"unit": "second", "cost": 0.05})
            ]

            async def execute(self, capability, inputs, config, credentials, *, idempotency_key=""):
                result = await call_my_api(inputs, credentials["API_KEY"])
                return {"video_url": result["url"], "__usage__": [{"usage_type": "video_seconds", "quantity": 10}]}
    """

    name: str = ""
    display_name: str = ""
    version: str = "1.0.0"
    capabilities: list[Capability] = []
    retry_policy: dict = {"max_attempts": 3, "backoff": "exponential"}
    idempotent: bool = True

    @abstractmethod
    async def execute(
        self,
        capability: str,
        inputs: dict,
        config: dict,
        credentials: dict[str, str],
        *,
        idempotency_key: str = "",
    ) -> dict:
        """Execute a single provider call. Returns JSON-serializable output."""
        ...

    async def health_check(self) -> HealthCheck:
        """Optional health check."""
        return HealthCheck(status="healthy", message="Not implemented")

    async def validate_config(self, config: dict) -> list[str]:
        """Validate config. Returns list of errors (empty = valid)."""
        return []

    async def validate_credentials(self, credentials: dict[str, str]) -> bool:
        """Validate credentials work."""
        return True

    def supports_capability(self, capability: str) -> bool:
        return any(c.key == capability for c in self.capabilities)


class EcosystemSourceAdapter(ABC):
    """Base class for third-party ecosystem data source adapters.

    Example::

        class MyTalentSource(EcosystemSourceAdapter):
            name = "my-talent-db"
            source_type = "talent_directory"

            async def fetch_records(self, config, credentials, *, since=None, limit=100):
                data = await call_my_api(config["base_url"], credentials["API_KEY"], since=since)
                return [SourceRecord(external_id=r["id"], data=r, source_type="talent_directory") for r in data]
    """

    name: str = ""
    source_type: str = ""
    version: str = "1.0.0"
    provenance_tracking: bool = True
    ingestion_rate_limit: int = 1000

    @abstractmethod
    async def fetch_records(
        self,
        config: dict,
        credentials: dict[str, str],
        *,
        since: str | None = None,
        limit: int = 100,
    ) -> list[SourceRecord]:
        """Pull records from the external source."""
        ...

    async def validate_config(self, config: dict) -> list[str]:
        return []

    async def health_check(self) -> HealthCheck:
        return HealthCheck(status="healthy")
