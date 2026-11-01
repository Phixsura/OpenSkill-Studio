"""API Consumer Data Residency — manage data residency requirements per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ResidencyConfig:
    consumer_id: str
    primary_region: str  # "us-east", "eu-west", "ap-south", etc.
    allowed_regions: list[str] = field(default_factory=list)
    data_types: list[str] = field(default_factory=list)  # "pii", "financial", "health", "general"
    compliance_frameworks: list[str] = field(default_factory=list)  # "gdpr", "hipaa", "ccpa", "sox"

VALID_REGIONS = {"us-east", "us-west", "eu-west", "eu-central", "ap-south", "ap-east", "ap-southeast"}
VALID_DATA_TYPES = {"pii", "financial", "health", "general", "sensitive"}
VALID_FRAMEWORKS = {"gdpr", "hipaa", "ccpa", "sox", "pci-dss", "iso27001"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiDataResidency:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], ResidencyConfig] = {}

    def configure(self, installation_id: str, config: ResidencyConfig) -> ResidencyConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if config.primary_region not in VALID_REGIONS: raise ValueError(f"Invalid region: {config.primary_region}")
        invalid_regions = set(config.allowed_regions) - VALID_REGIONS
        if invalid_regions: raise ValueError(f"Invalid regions: {invalid_regions}")
        if config.primary_region not in config.allowed_regions:
            config.allowed_regions.append(config.primary_region)
        invalid_types = set(config.data_types) - VALID_DATA_TYPES
        if invalid_types: raise ValueError(f"Invalid data types: {invalid_types}")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def check_region(self, installation_id: str, consumer_id: str, region: str) -> bool:
        config = self._configs.get((installation_id, consumer_id))
        if config is None: return True  # no config = no restriction
        return region in config.allowed_regions

    def get_config(self, installation_id: str, consumer_id: str) -> ResidencyConfig | None:
        return self._configs.get((installation_id, consumer_id))

    def consumers_in_region(self, installation_id: str, region: str) -> list[str]:
        return [cid for (inst, cid), c in self._configs.items() if inst == installation_id and region in c.allowed_regions]

    def list_configs(self, installation_id: str) -> list[ResidencyConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
