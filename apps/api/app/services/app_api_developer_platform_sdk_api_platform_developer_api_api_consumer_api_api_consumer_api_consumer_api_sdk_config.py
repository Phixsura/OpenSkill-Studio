"""Consumer API SDK Config — generate and manage SDK configurations per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class SDKConfig:
    config_id: str
    consumer_id: str
    language: str  # "typescript", "python", "go", "java", "ruby"
    base_url: str = ""
    api_version: str = "v1"
    timeout_ms: int = 30000
    retry_count: int = 3
    retry_delay_ms: int = 1000
    custom_headers: dict[str, str] = field(default_factory=dict)

VALID_LANGUAGES = {"typescript", "python", "go", "java", "ruby", "csharp", "php"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSdkConfig:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], SDKConfig] = {}

    def create(self, installation_id: str, config: SDKConfig) -> SDKConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.language not in VALID_LANGUAGES:
            raise ValueError(f"Unsupported language: {config.language}")
        if config.timeout_ms < 1000:
            raise ValueError("timeout_ms must be at least 1000")
        if config.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        key = (installation_id, config.config_id)
        self._configs[key] = config
        log.info("sdk_config_created", installation_id=installation_id, config_id=config.config_id, lang=config.language)
        return config

    def get(self, installation_id: str, config_id: str) -> SDKConfig | None:
        return self._configs.get((installation_id, config_id))

    def generate_snippet(self, installation_id: str, config_id: str) -> str:
        config = self._configs.get((installation_id, config_id))
        if not config:
            raise ValueError("Config not found")
        if config.language == "typescript":
            return f'const client = new APIClient({{\n  baseUrl: "{config.base_url}",\n  version: "{config.api_version}",\n  timeout: {config.timeout_ms},\n  retries: {config.retry_count},\n}});'
        elif config.language == "python":
            return f'client = APIClient(\n    base_url="{config.base_url}",\n    version="{config.api_version}",\n    timeout={config.timeout_ms / 1000},\n    retries={config.retry_count},\n)'
        else:
            return json.dumps({"base_url": config.base_url, "version": config.api_version, "timeout_ms": config.timeout_ms, "retries": config.retry_count}, indent=2)

    def list_configs(self, installation_id: str, consumer_id: str) -> list[SDKConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id and c.consumer_id == consumer_id]
