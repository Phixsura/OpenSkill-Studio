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
    """OneRoster 1.2 Rostering consumer (pull-only; the REST binding permits
    reading only — S3.2). OAuth2 client-credentials, offset pagination.

    State shape: {"endpoint_offset": N} per model; a run reads every page
    (tombstones ride the backfill trigger, §11.3)."""

    key = "oneroster"
    capabilities = frozenset({"roster.read"})

    # canonical model -> (endpoint, response collection key)
    MODEL_ENDPOINTS = {
        "roster.term": ("academicSessions", "academicSessions"),
        "roster.class": ("classes", "classes"),
        "roster.enrollment": ("enrollments", "enrollments"),
        "roster.user": ("users", "users"),
    }

    async def ping(self, ctx: ConnCtx) -> None:
        from app.exceptions import AppError

        if not ctx.base_url:
            raise AppError("CONNECTION_CONFIG_INVALID", "base_url is required", 422)
        validate_egress_url(ctx.base_url)
        validate_egress_url(ctx.config["token_url"])

    async def _token(self, ctx: ConnCtx) -> str:
        from urllib.parse import urlencode

        from app.exceptions import AppError

        secret = await ctx.get_secret()
        resp = await ctx.egress.request(
            "POST",
            ctx.config["token_url"],
            headers={"content-type": "application/x-www-form-urlencoded"},
            content=urlencode(
                {
                    "grant_type": "client_credentials",
                    "client_id": secret.get("client_id", ""),
                    "client_secret": secret.get("client_secret", ""),
                    "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster.readonly",
                }
            ).encode(),
        )
        if resp.status_code != 200:
            raise AppError("CONNECTION_AUTH_REJECTED", "OneRoster token refused", 422)
        token = resp.json().get("access_token", "")
        if not token:
            raise AppError("CONNECTION_AUTH_REJECTED", "No access_token in response", 422)
        return token

    @staticmethod
    def _map_record(model: str, item: dict) -> dict:
        """OneRoster JSON -> canonical payload; sourcedId -> external_id.
        A MappingProfile can replace/extend this via the sync profile — this
        is the sensible default so OneRoster works with zero mapping config."""
        out: dict = {"external_id": str(item.get("sourcedId", ""))}
        if model == "roster.term":
            out.update(
                {
                    "name": item.get("title"),
                    "start_date": item.get("startDate"),
                    "end_date": item.get("endDate"),
                    "school_year": item.get("schoolYear"),
                }
            )
        elif model == "roster.class":
            out.update(
                {
                    "title": item.get("title"),
                    "course_code": item.get("classCode"),
                    "term_external_id": ((item.get("terms") or [{}])[0] or {}).get("sourcedId"),
                    "school_external_id": (item.get("school") or {}).get("sourcedId"),
                    "subjects": item.get("subjects") or [],
                    "grades": item.get("grades") or [],
                }
            )
        elif model == "roster.enrollment":
            out.update(
                {
                    "class_external_id": (item.get("class") or {}).get("sourcedId"),
                    "user_external_id": (item.get("user") or {}).get("sourcedId"),
                    "role": item.get("role"),
                    "begin_date": item.get("beginDate"),
                    "end_date": item.get("endDate"),
                    "primary": item.get("primary"),
                }
            )
        elif model == "roster.user":
            out.update(
                {
                    "email": item.get("email"),
                    "display_name": (
                        f"{item.get('givenName', '')} {item.get('familyName', '')}".strip()
                        or item.get("username")
                    ),
                    "role": item.get("role"),
                    "username": item.get("username"),
                }
            )
        return out

    async def read(self, ctx: ConnCtx, model: str, state: dict):
        from app.exceptions import AppError

        endpoint = self.MODEL_ENDPOINTS.get(model)
        if endpoint is None:
            raise AppError("SYNC_PROFILE_INVALID", f"oneroster cannot read {model}", 422)
        path, collection_key = endpoint
        page_size = int(ctx.config.get("page_size", 100))
        token = await self._token(ctx)
        offset = int(state.get("endpoint_offset", 0))
        base = (ctx.base_url or "").rstrip("/")
        while True:
            url = f"{base}/{path}?limit={page_size}&offset={offset}"
            resp = await ctx.egress.request(
                "GET", url, headers={"authorization": f"Bearer {token}"}
            )
            if resp.status_code == 401:
                raise AppError("CONNECTION_AUTH_REJECTED", "OneRoster 401", 422)
            if resp.status_code != 200:
                raise AppError("CONNECTION_PING_FAILED", f"OneRoster {resp.status_code}", 422)
            items = resp.json().get(collection_key, []) or []
            records = [self._map_record(model, i) for i in items if isinstance(i, dict)]
            offset += len(items)
            last_page = len(items) < page_size
            # Mid-run checkpoints carry the live offset (a crashed run
            # resumes mid-pagination); the FINAL batch resets to 0 so the
            # next run re-reads the full collection (offset pagination has
            # no durable delta cursor — unchanged rows dedupe by raw_hash).
            yield {
                "records": records,
                "state": {"endpoint_offset": 0 if last_page else offset},
            }
            if last_page:
                break


CONNECTORS: dict[str, Connector] = {
    c.key: c  # type: ignore[misc]
    for c in (GenericWebhookConnector(), GenericRestConnector(), OneRosterConnector())
}
