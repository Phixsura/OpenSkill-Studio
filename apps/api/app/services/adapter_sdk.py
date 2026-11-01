"""Third-party Provider Adapter SDK (ADR-016 Part H).

Formalizes the ProviderAdapterBase contract for external developers.
Adds health check, capability declaration, pricing metadata, retry policy,
and registration into the adapter registry.
"""

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog

log = structlog.get_logger()


# ── Data classes ─────────────────────────────────────────


@dataclass
class Capability:
    """Declares one capability an adapter provides."""

    key: str
    input_schema: dict = field(default_factory=dict)
    output_schema: dict = field(default_factory=dict)
    pricing: dict = field(default_factory=dict)  # {"unit": "image", "cost_per_unit": 0.05}


@dataclass
class HealthCheck:
    status: str  # "healthy", "degraded", "unhealthy"
    latency_ms: int = 0
    message: str | None = None
    checked_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


@dataclass
class AdapterMetadata:
    """Serializable metadata for registry listing."""

    name: str
    display_name: str
    version: str
    capabilities: list[dict]
    retry_policy: dict
    idempotent: bool
    health_check_supported: bool


# ── Base class ───────────────────────────────────────────


class ProviderAdapterSDK(ABC):
    """Third-party provider adapter base class.

    Extends the internal ProviderAdapterBase with:
    - Declarative capabilities with input/output schemas
    - Health check contract
    - Retry and idempotency declarations
    - Pricing metadata for marketplace listings
    - HTTP client helper with timeout and error handling
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
        """Execute a single provider call.

        Args:
            capability: The capability key (must be in self.capabilities)
            inputs: Input data matching the capability's input_schema
            config: Installation-specific configuration
            credentials: Decrypted secrets (injected at call time, never stored)
            idempotency_key: For safe retries

        Returns:
            JSON-serializable dict. May include "__usage__" key for billing:
            {"__usage__": [{"usage_type": "image_generation", "quantity": 1}]}
        """

    async def health_check(self) -> HealthCheck:
        """Optional health check. Override to implement."""
        return HealthCheck(status="healthy", message="Health check not implemented")

    async def validate_config(self, config: dict) -> list[str]:
        """Validate installation config. Returns list of error messages (empty = valid)."""
        return []

    async def validate_credentials(self, credentials: dict[str, str]) -> bool:
        """Validate that credentials work. Override to implement."""
        return True

    def get_metadata(self) -> AdapterMetadata:
        """Return serializable metadata for registry."""
        return AdapterMetadata(
            name=self.name,
            display_name=self.display_name,
            version=self.version,
            capabilities=[
                {
                    "key": c.key,
                    "input_schema": c.input_schema,
                    "output_schema": c.output_schema,
                    "pricing": c.pricing,
                }
                for c in self.capabilities
            ],
            retry_policy=self.retry_policy,
            idempotent=self.idempotent,
            health_check_supported=type(self).health_check is not ProviderAdapterSDK.health_check,
        )

    def supports_capability(self, capability: str) -> bool:
        return any(c.key == capability for c in self.capabilities)


# ── Ecosystem Source Adapter SDK (Part I) ────────────────


@dataclass
class SourceRecord:
    """A single record from an external data source."""

    external_id: str
    data: dict
    source_type: str
    fetched_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    checksum: str = ""

    def __post_init__(self):
        if not self.checksum:
            self.checksum = hashlib.sha256(
                json.dumps(self.data, sort_keys=True).encode()
            ).hexdigest()[:16]


class EcosystemSourceAdapter(ABC):
    """Base class for third-party ecosystem data source adapters.

    Extends ADR-015 ecosystem intelligence for external sources with:
    - Incremental fetch (since cursor)
    - Rate limiting
    - Provenance tracking
    - SSRF protection via sandbox network policy
    - Parser versioning
    """

    name: str = ""
    source_type: str = ""  # e.g. "talent_directory", "job_board", "credential_registry"
    version: str = "1.0.0"
    provenance_tracking: bool = True
    ingestion_rate_limit: int = 1000  # records per hour

    @abstractmethod
    async def fetch_records(
        self,
        config: dict,
        credentials: dict[str, str],
        *,
        since: str | None = None,
        limit: int = 100,
    ) -> list[SourceRecord]:
        """Pull records from the external source.

        Args:
            config: Source configuration (base URL, filters, etc.)
            credentials: Decrypted API keys/tokens
            since: Cursor for incremental fetch (ISO timestamp or opaque token)
            limit: Max records per batch

        Returns:
            List of SourceRecord with external_id for dedup
        """

    async def validate_config(self, config: dict) -> list[str]:
        """Validate source configuration before activation."""
        return []

    async def health_check(self) -> HealthCheck:
        """Check source availability."""
        return HealthCheck(status="healthy")

    def get_metadata(self) -> dict:
        return {
            "name": self.name,
            "source_type": self.source_type,
            "version": self.version,
            "provenance_tracking": self.provenance_tracking,
            "ingestion_rate_limit": self.ingestion_rate_limit,
        }


# ── Adapter Registry ────────────────────────────────────

# Third-party adapters register here at app startup
_THIRD_PARTY_ADAPTERS: dict[str, ProviderAdapterSDK] = {}
_THIRD_PARTY_SOURCES: dict[str, EcosystemSourceAdapter] = {}


def register_adapter(adapter: ProviderAdapterSDK) -> None:
    """Register a third-party provider adapter."""
    if not adapter.name:
        raise ValueError("Adapter must have a name")
    _THIRD_PARTY_ADAPTERS[adapter.name] = adapter
    log.info("adapter_registered", name=adapter.name, version=adapter.version)


def register_source(source: EcosystemSourceAdapter) -> None:
    """Register a third-party ecosystem source adapter."""
    if not source.name:
        raise ValueError("Source adapter must have a name")
    _THIRD_PARTY_SOURCES[source.name] = source
    log.info("source_adapter_registered", name=source.name, type=source.source_type)


def get_adapter(name: str) -> ProviderAdapterSDK | None:
    return _THIRD_PARTY_ADAPTERS.get(name)


def get_source(name: str) -> EcosystemSourceAdapter | None:
    return _THIRD_PARTY_SOURCES.get(name)


def list_adapters() -> list[AdapterMetadata]:
    return [a.get_metadata() for a in _THIRD_PARTY_ADAPTERS.values()]


def list_sources() -> list[dict]:
    return [s.get_metadata() for s in _THIRD_PARTY_SOURCES.values()]
