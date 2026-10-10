"""In-repo provider catalog + connector registry (ADR-018 §4.1/§13).

The catalog dict is the source of truth; ``sync_provider_catalog`` upserts it
into intg_providers at startup/migration time. Connector implementations are
keyed by the same provider key — CI asserts the two registries agree
(every provider key has a connector, capability sets equal).

v1 ships protocol/skeleton connectors only; engine connectors (oneroster,
warehouse_s3, ...) land in later phases behind the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from app.integrations.security import EgressClient, validate_egress_url

# ── Provider catalog (code-seeded; bump "version" on any breaking change) ──

PROVIDER_CATALOG: dict[str, dict[str, Any]] = {
    "generic_webhook": {
        "category": "generic",
        "auth_mode": "none",
        "display_name": "Generic signed webhook",
        "capabilities": ["events.deliver"],
        "config_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {},
        },
        "version": 1,
    },
    "generic_rest": {
        "category": "generic",
        "auth_mode": "api_key",
        "display_name": "Generic REST API",
        "capabilities": [],
        "config_schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "auth_header": {
                    "type": "string",
                    "maxLength": 100,
                    "description": "Header name carrying the API key",
                    "default": "Authorization",
                },
            },
        },
        "version": 1,
    },
    "oneroster": {
        "category": "roster",
        "auth_mode": "oauth2_cc",
        "display_name": "OneRoster 1.2 (SIS)",
        "capabilities": ["roster.read"],
        "config_schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["token_url"],
            "properties": {
                "token_url": {"type": "string", "maxLength": 500},
                "page_size": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 500,
                    "default": 100,
                },
            },
        },
        "version": 1,
    },
}


# ── Connector interface (§13) ──


@dataclass
class ConnCtx:
    """Everything a connector may touch. ``get_secret`` decrypts inside the
    call and returns individual fields — the engine never holds the blob.
    Connectors cannot construct their own HTTP client (egress is injected)."""

    connection_id: str
    config: dict[str, Any]
    base_url: str | None
    egress: EgressClient = field(default_factory=EgressClient)
    _secret_loader: Any = None  # async () -> dict[str, str]

    async def get_secret(self) -> dict[str, str]:
        if self._secret_loader is None:
            return {}
        return await self._secret_loader()


class Connector(Protocol):
    key: str
    capabilities: frozenset[str]

    async def ping(self, ctx: ConnCtx) -> None:
        """Health/credential check; raise AppError on failure."""


class GenericWebhookConnector:
    """Delivery target for the event mesh (P2). Ping validates reachability
    of nothing — subscriptions carry their own URLs — so it only re-screens
    the optional base_url."""

    key = "generic_webhook"
    capabilities = frozenset({"events.deliver"})

    async def ping(self, ctx: ConnCtx) -> None:
        if ctx.base_url:
            validate_egress_url(ctx.base_url)


class GenericRestConnector:
    """Minimal REST connector: ping GETs the base_url root with the API key
    header and accepts any non-5xx response (auth semantics differ per API;
    a 401 is surfaced as a credential problem by the service layer)."""

    key = "generic_rest"
    capabilities = frozenset()

    async def ping(self, ctx: ConnCtx) -> None:
        from app.exceptions import AppError

        if not ctx.base_url:
            raise AppError("CONNECTION_CONFIG_INVALID", "base_url is required for ping", 422)
        secret = await ctx.get_secret()
        header = ctx.config.get("auth_header", "Authorization")
        headers = {header: secret.get("api_key", "")} if secret else {}
        resp = await ctx.egress.request("GET", ctx.base_url, headers=headers)
        if resp.status_code == 401 or resp.status_code == 403:
            raise AppError("CONNECTION_AUTH_REJECTED", "Provider rejected the credential", 422)
        if resp.status_code >= 500:
            raise AppError("CONNECTION_PING_FAILED", f"Provider returned {resp.status_code}", 422)


class OneRosterConnector:
    """P6 fills in read(); P1 ships ping (token endpoint reachability)."""

    key = "oneroster"
    capabilities = frozenset({"roster.read"})

    async def ping(self, ctx: ConnCtx) -> None:
        from app.exceptions import AppError

        if not ctx.base_url:
            raise AppError("CONNECTION_CONFIG_INVALID", "base_url is required", 422)
        validate_egress_url(ctx.base_url)
        validate_egress_url(ctx.config["token_url"])


CONNECTORS: dict[str, Connector] = {
    c.key: c  # type: ignore[misc]
    for c in (GenericWebhookConnector(), GenericRestConnector(), OneRosterConnector())
}
