"""SDK Client — Python client library for the OpenSkill Extension API.

Provides a typed, ergonomic client for extension developers to interact
with the platform APIs: manage extensions, webhooks, config, and events.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class SDKConfig:
    api_key: str
    base_url: str = "https://api.openskill.dev/v1"
    timeout_seconds: int = 30
    retry_count: int = 3


class OpenSkillSDK:
    """Python SDK client for the OpenSkill Developer Platform."""

    def __init__(self, config: SDKConfig):
        self.config = config
        self._call_log: list[dict] = []

    def _call(self, method: str, endpoint: str, data: dict | None = None) -> dict:
        """Simulate an API call (real impl would use httpx)."""
        call = {
            "method": method,
            "endpoint": f"{self.config.base_url}{endpoint}",
            "data": data,
            "api_key_prefix": self.config.api_key[:8] + "...",
        }
        self._call_log.append(call)
        return {"ok": True, "endpoint": endpoint, "method": method}

    # Extension Management
    def get_extension(self, extension_id: str) -> dict:
        return self._call("GET", f"/extensions/{extension_id}")

    def list_extensions(self, author: str | None = None) -> dict:
        params = f"?author={author}" if author else ""
        return self._call("GET", f"/extensions{params}")

    def publish_version(self, extension_id: str, version: str, changelog: str) -> dict:
        return self._call("POST", f"/extensions/{extension_id}/versions",
                          {"version": version, "changelog": changelog})

    # Webhook Management
    def create_webhook(self, url: str, events: list[str]) -> dict:
        return self._call("POST", "/webhooks", {"url": url, "events": events})

    def list_webhooks(self) -> dict:
        return self._call("GET", "/webhooks")

    def delete_webhook(self, webhook_id: str) -> dict:
        return self._call("DELETE", f"/webhooks/{webhook_id}")

    # Configuration
    def get_config(self, extension_id: str, org_id: str) -> dict:
        return self._call("GET", f"/extensions/{extension_id}/config/{org_id}")

    def set_config(self, extension_id: str, org_id: str, config: dict) -> dict:
        return self._call("PUT", f"/extensions/{extension_id}/config/{org_id}", config)

    # Events
    def emit_event(self, event_type: str, payload: dict) -> dict:
        return self._call("POST", "/events", {"type": event_type, "payload": payload})

    # Analytics
    def get_analytics(self, extension_id: str, period: str = "7d") -> dict:
        return self._call("GET", f"/extensions/{extension_id}/analytics?period={period}")

    # Health
    def report_health(self, extension_id: str, status: str, response_ms: float) -> dict:
        return self._call("POST", f"/extensions/{extension_id}/health",
                          {"status": status, "response_ms": response_ms})

    def get_call_log(self) -> list[dict]:
        return list(self._call_log)
