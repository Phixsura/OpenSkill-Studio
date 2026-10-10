"""Connection lifecycle service (ADR-018 §4).

Router → Schema → Service → Model layering: all business rules live here.
Cross-tenant access is answered with 404 (never 403) — R88 uniform-404.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt_credentials, encrypt_credentials
from app.exceptions import AppError
from app.integrations.models import (
    CONNECTION_TRANSITIONS,
    CREDENTIAL_KINDS,
    DEGRADE_AFTER_FAILURES,
    IntegrationConnection,
    IntegrationConnectionCredential,
    IntegrationProvider,
)
from app.integrations.registry import CONNECTORS, PROVIDER_CATALOG, ConnCtx
from app.integrations.security import validate_egress_url

_MAX_CONFIG_BYTES = 16_384
_MAX_SECRET_VALUE_LEN = 4_096


def _not_found() -> AppError:
    return AppError("CONNECTION_NOT_FOUND", "Connection not found", 404)


def _validate_config(config: dict, schema: dict) -> list[str]:
    """Bounded JSON-Schema subset validator (object/required/
    additionalProperties/type/maxLength/minimum/maximum). Returns a list of
    problems — empty means valid. Deliberately small: provider config
    schemas are in-repo data, not arbitrary user schemas."""
    problems: list[str] = []
    props: dict[str, Any] = schema.get("properties", {})
    if schema.get("additionalProperties") is False:
        for key in config:
            if key not in props:
                problems.append(f"config.{key}: unknown key")
    for key in schema.get("required", []):
        if key not in config:
            problems.append(f"config.{key}: required")
    type_map = {"string": str, "integer": int, "boolean": bool, "object": dict}
    for key, spec in props.items():
        if key not in config:
            continue
        val = config[key]
        expected = type_map.get(spec.get("type", ""))
        # bool is an int subclass — reject True for integer fields explicitly.
        if expected is int and isinstance(val, bool):
            problems.append(f"config.{key}: expected integer")
            continue
        if expected is not None and not isinstance(val, expected):
            problems.append(f"config.{key}: expected {spec['type']}")
            continue
        if isinstance(val, str) and len(val) > spec.get("maxLength", 10_000):
            problems.append(f"config.{key}: too long")
        if isinstance(val, int) and not isinstance(val, bool):
            if "minimum" in spec and val < spec["minimum"]:
                problems.append(f"config.{key}: below minimum {spec['minimum']}")
            if "maximum" in spec and val > spec["maximum"]:
                problems.append(f"config.{key}: above maximum {spec['maximum']}")
    return problems


class ConnectionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── catalog ──

    async def sync_provider_catalog(self) -> int:
        """Upsert the in-repo catalog into intg_providers. Idempotent; rows
        are never deleted (missing keys are disabled). Returns changed count."""
        changed = 0
        result = await self.db.execute(select(IntegrationProvider))
        existing = {p.key: p for p in result.scalars()}
        for key, spec in PROVIDER_CATALOG.items():
            row = existing.get(key)
            if row is None:
                self.db.add(
                    IntegrationProvider(
                        key=key,
                        category=spec["category"],
                        auth_mode=spec["auth_mode"],
                        display_name=spec["display_name"],
                        capabilities=spec["capabilities"],
                        config_schema=spec["config_schema"],
                        version=spec["version"],
                        enabled=True,
                    )
                )
                changed += 1
            elif row.version != spec["version"] or not row.enabled:
                row.category = spec["category"]
                row.auth_mode = spec["auth_mode"]
                row.display_name = spec["display_name"]
                row.capabilities = spec["capabilities"]
                row.config_schema = spec["config_schema"]
                row.version = spec["version"]
                row.enabled = True
                changed += 1
        for key, row in existing.items():
            if key not in PROVIDER_CATALOG and row.enabled:
                row.enabled = False
                changed += 1
        return changed

    async def list_providers(self) -> list[IntegrationProvider]:
        result = await self.db.execute(
            select(IntegrationProvider)
            .where(IntegrationProvider.enabled.is_(True))
            .order_by(IntegrationProvider.key)
        )
        return list(result.scalars())

    # ── connections ──

    async def _get_provider_by_key(self, key: str) -> IntegrationProvider:
        result = await self.db.execute(
            select(IntegrationProvider).where(IntegrationProvider.key == key)
        )
        provider = result.scalar_one_or_none()
        if provider is None:
            raise AppError("PROVIDER_NOT_FOUND", f"Unknown provider: {key}", 404)
        if not provider.enabled:
            raise AppError("PROVIDER_DISABLED", f"Provider disabled: {key}", 409)
        return provider

    def _screen_config(self, config: dict, provider: IntegrationProvider) -> None:
        import json

        if len(json.dumps(config)) > _MAX_CONFIG_BYTES:
            raise AppError("CONNECTION_CONFIG_INVALID", "config too large", 422)
        problems = _validate_config(config, provider.config_schema or {})
        if problems:
            raise AppError(
                "CONNECTION_CONFIG_INVALID",
                "config does not match provider schema",
                422,
                details=problems,
            )

    async def create(
        self,
        org_id: str,
        *,
        provider_key: str,
        name: str,
        config: dict,
        base_url: str | None,
        created_by: str,
    ) -> IntegrationConnection:
        provider = await self._get_provider_by_key(provider_key)
        self._screen_config(config, provider)
        if base_url is not None:
            validate_egress_url(base_url)
        dup = await self.db.execute(
            select(IntegrationConnection.id).where(
                IntegrationConnection.org_id == org_id,
                IntegrationConnection.name == name,
            )
        )
        if dup.scalar_one_or_none() is not None:
            raise AppError("CONNECTION_NAME_TAKEN", "A connection with this name exists", 409)
        conn = IntegrationConnection(
            org_id=org_id,
            provider_id=provider.id,
            provider_version=provider.version,
            name=name,
            status="pending",
            config=config,
            base_url=base_url,
            health={},
            created_by=created_by,
        )
        self.db.add(conn)
        await self.db.flush()
        # server_default timestamps must be loaded eagerly — an async lazy
        # load at response-serialization time raises MissingGreenlet.
        await self.db.refresh(conn)
        return conn

    async def get(self, org_id: str, connection_id: str) -> IntegrationConnection:
        conn = await self.db.get(IntegrationConnection, connection_id)
        # Uniform 404: wrong id and foreign-tenant id are indistinguishable.
        if conn is None or conn.org_id != org_id:
            raise _not_found()
        return conn

    async def list(self, org_id: str) -> list[IntegrationConnection]:
        result = await self.db.execute(
            select(IntegrationConnection)
            .where(IntegrationConnection.org_id == org_id)
            .order_by(IntegrationConnection.created_at.desc())
        )
        return list(result.scalars())

    async def update(
        self,
        org_id: str,
        connection_id: str,
        *,
        name: str | None = None,
        config: dict | None = None,
        base_url: str | None = None,
        status: str | None = None,
    ) -> IntegrationConnection:
        conn = await self.get(org_id, connection_id)
        if name is not None and name != conn.name:
            dup = await self.db.execute(
                select(IntegrationConnection.id).where(
                    IntegrationConnection.org_id == org_id,
                    IntegrationConnection.name == name,
                    IntegrationConnection.id != connection_id,
                )
            )
            if dup.scalar_one_or_none() is not None:
                raise AppError("CONNECTION_NAME_TAKEN", "A connection with this name exists", 409)
            conn.name = name
        if config is not None:
            provider = await self.db.get(IntegrationProvider, conn.provider_id)
            assert provider is not None  # RESTRICT FK
            self._screen_config(config, provider)
            conn.config = config
        if base_url is not None:
            validate_egress_url(base_url)
            conn.base_url = base_url
        if status is not None:
            # Admin surface accepts only disable / re-enable (§4.2); the
            # machine-managed states are not settable from the API.
            if status not in ("disabled", "pending"):
                raise AppError("CONNECTION_STATUS_INVALID", "status must be disabled|pending", 422)
            if status not in CONNECTION_TRANSITIONS[conn.status]:
                raise AppError(
                    "CONNECTION_STATUS_INVALID",
                    f"cannot move {conn.status} -> {status}",
                    409,
                )
            conn.status = status
        await self.db.flush()
        return conn

    async def upgrade(self, org_id: str, connection_id: str) -> IntegrationConnection:
        """Explicit provider-version upgrade (ADR §19): re-validates config
        against the NEW schema and re-checks connector presence — surfaces
        CONNECTION_CONFIG_INVALID / CAPABILITY_MISSING, never silent."""
        conn = await self.get(org_id, connection_id)
        provider = await self.db.get(IntegrationProvider, conn.provider_id)
        assert provider is not None
        if conn.provider_version == provider.version:
            return conn  # already current — idempotent
        if not provider.enabled:
            raise AppError("PROVIDER_DISABLED", f"Provider disabled: {provider.key}", 409)
        self._screen_config(conn.config or {}, provider)
        if CONNECTORS.get(provider.key) is None:
            raise AppError("CAPABILITY_MISSING", "No connector registered", 409)
        conn.provider_version = provider.version
        await self.db.flush()
        return conn

    async def delete(self, org_id: str, connection_id: str) -> None:
        conn = await self.get(org_id, connection_id)
        await self.db.delete(conn)
        await self.db.flush()

    # ── credentials (write-only) ──

    async def set_credential(
        self,
        org_id: str,
        connection_id: str,
        *,
        kind: str,
        values: dict[str, str],
        expires_at: datetime | None,
    ) -> IntegrationConnectionCredential:
        conn = await self.get(org_id, connection_id)
        if kind not in CREDENTIAL_KINDS:
            raise AppError("CREDENTIAL_KIND_INVALID", f"kind must be one of {sorted(CREDENTIAL_KINDS)}", 422)
        for k, v in values.items():
            if not isinstance(v, str) or len(v) > _MAX_SECRET_VALUE_LEN or len(k) > 100:
                raise AppError("CREDENTIAL_VALUE_INVALID", "credential values malformed", 422)
        ciphertext = encrypt_credentials(values)
        result = await self.db.execute(
            select(IntegrationConnectionCredential).where(
                IntegrationConnectionCredential.connection_id == connection_id
            )
        )
        cred = result.scalar_one_or_none()
        if cred is None:
            cred = IntegrationConnectionCredential(
                connection_id=connection_id,
                kind=kind,
                ciphertext=ciphertext,
                expires_at=expires_at,
            )
            self.db.add(cred)
        else:
            cred.kind = kind
            cred.ciphertext = ciphertext
            cred.expires_at = expires_at
        # Replacing credentials on an errored connection re-opens it for a
        # fresh ping (§4.2: error -> pending).
        if conn.status == "error":
            conn.status = "pending"
        await self.db.flush()
        await self.db.refresh(cred)  # rotated_at is server-generated
        return cred

    async def _secret_loader(self, connection_id: str):
        async def load() -> dict[str, str]:
            result = await self.db.execute(
                select(IntegrationConnectionCredential).where(
                    IntegrationConnectionCredential.connection_id == connection_id
                )
            )
            cred = result.scalar_one_or_none()
            if cred is None:
                return {}
            return decrypt_credentials(cred.ciphertext)

        return load

    # ── health / ping ──

    async def ping(self, org_id: str, connection_id: str) -> IntegrationConnection:
        conn = await self.get(org_id, connection_id)
        provider = await self.db.get(IntegrationProvider, conn.provider_id)
        assert provider is not None
        connector = CONNECTORS.get(provider.key)
        if connector is None:
            raise AppError("PROVIDER_DISABLED", "No connector registered", 409)
        ctx = ConnCtx(
            connection_id=conn.id,
            config=conn.config or {},
            base_url=conn.base_url,
            _secret_loader=await self._secret_loader(conn.id),
        )
        try:
            await connector.ping(ctx)
        except AppError as exc:
            self._record_failure(conn, exc.code)
            await self.db.flush()
            raise
        self._record_success(conn)
        await self.db.flush()
        return conn

    def _record_success(self, conn: IntegrationConnection) -> None:
        health = dict(conn.health or {})
        health["last_ok_at"] = datetime.now(UTC).isoformat()
        health["consecutive_failures"] = 0
        health.pop("last_error_class_prev", None)
        conn.health = health
        if conn.status in ("pending", "degraded"):
            conn.status = "active"

    def _record_failure(self, conn: IntegrationConnection, error_class: str) -> None:
        health = dict(conn.health or {})
        health["last_error_at"] = datetime.now(UTC).isoformat()
        health["last_error_class"] = error_class
        failures = int(health.get("consecutive_failures", 0)) + 1
        health["consecutive_failures"] = failures
        conn.health = health
        if error_class == "CONNECTION_AUTH_REJECTED":
            # Second consecutive auth rejection parks the connection (§4.2).
            if health.get("last_error_class_prev") == "CONNECTION_AUTH_REJECTED":
                conn.status = "error"
        elif conn.status == "active" and failures >= DEGRADE_AFTER_FAILURES:
            conn.status = "degraded"
        health["last_error_class_prev"] = error_class
        conn.health = health
