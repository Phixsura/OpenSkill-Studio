"""Provider connection/offering management (ADR-011).

Credential values are write-only: encrypted on create/update, never returned.
Only the workflow executor decrypts them, immediately before a provider call.
"""

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encrypt_credentials
from app.exceptions import AppError
from app.models.capability import CapabilityTag
from app.models.provider import (
    OrgCredential,
    ProviderAdapter,
    ProviderConnection,
    ProviderModelOffering,
)

log = structlog.get_logger()

MAX_CONNECTIONS_PER_ORG = 25
MAX_OFFERINGS_PER_CONNECTION = 50

# update_connection sentinel: the endpoint dumps with exclude_unset, so an
# absent `credentials` field never reaches the service — a None that DOES
# arrive is an explicit null from the client (detach), not "unchanged".
_UNSET: object = object()


class ProviderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── Capabilities (read-only catalog) ──────────────────

    async def list_capabilities(self) -> list[CapabilityTag]:
        result = await self.db.execute(
            select(CapabilityTag).where(CapabilityTag.is_platform.is_(True)).order_by(CapabilityTag.key)
        )
        return list(result.scalars().all())

    async def get_capability(self, key: str) -> CapabilityTag | None:
        result = await self.db.execute(select(CapabilityTag).where(CapabilityTag.key == key))
        return result.scalar_one_or_none()

    # ── Adapters (platform catalog, read-only) ────────────

    async def list_adapters(self) -> list[ProviderAdapter]:
        result = await self.db.execute(
            select(ProviderAdapter).where(ProviderAdapter.is_active.is_(True)).order_by(ProviderAdapter.key)
        )
        return list(result.scalars().all())

    # ── Connections ───────────────────────────────────────

    async def create_connection(
        self,
        org_id: str,
        adapter_id: str,
        name: str,
        config: dict,
        credentials: dict[str, str] | None,
        created_by: str,
    ) -> ProviderConnection:
        adapter = await self.db.get(ProviderAdapter, adapter_id)
        if adapter is None or not adapter.is_active:
            raise AppError("ADAPTER_NOT_FOUND", "Provider adapter not found", 404)

        # Reject credential field names smuggled into non-sensitive config (R3)
        cred_fields = set(adapter.credential_fields or [])
        leaked = cred_fields & set(config.keys())
        if leaked:
            raise AppError(
                "CREDENTIAL_IN_CONFIG",
                f"Credential fields must not appear in config: {', '.join(sorted(leaked))}",
                422,
            )

        # Enforce connection limit (FOR UPDATE on org row not needed — soft limit)
        count_r = await self.db.execute(
            select(func.count()).where(ProviderConnection.org_id == org_id)
        )
        if count_r.scalar_one() >= MAX_CONNECTIONS_PER_ORG:
            raise AppError(
                "CONNECTION_LIMIT_REACHED",
                f"Maximum {MAX_CONNECTIONS_PER_ORG} provider connections per organization",
                422,
            )

        credential_id = None
        if credentials:
            # Validate supplied fields against the adapter's declared fields
            unknown = set(credentials.keys()) - cred_fields
            if unknown:
                raise AppError(
                    "UNKNOWN_CREDENTIAL_FIELD",
                    f"Adapter does not declare credential fields: {', '.join(sorted(unknown))}",
                    422,
                )
            cred = OrgCredential(
                org_id=org_id,
                # Truncate: connection names may be up to 100 chars but the
                # OrgCredential.name column is String(100) — " credentials"
                # is 12 chars, so cap the prefix at 88
                name=f"{name[:88]} credentials",
                encrypted_data=encrypt_credentials(credentials),
                created_by=created_by,
            )
            self.db.add(cred)
            await self.db.flush()
            credential_id = cred.id

        conn = ProviderConnection(
            org_id=org_id,
            adapter_id=adapter_id,
            name=name,
            config=config,
            credential_id=credential_id,
            created_by=created_by,
        )
        self.db.add(conn)
        await self.db.flush()
        log.info("provider_connection_created", connection_id=conn.id, org_id=org_id, adapter=adapter.key)
        return conn

    async def list_connections(self, org_id: str) -> list[ProviderConnection]:
        result = await self.db.execute(
            select(ProviderConnection)
            .where(ProviderConnection.org_id == org_id)
            .order_by(ProviderConnection.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_connection(self, connection_id: str, org_id: str) -> ProviderConnection:
        conn = await self.db.get(ProviderConnection, connection_id)
        if conn is None or conn.org_id != org_id:
            raise AppError("CONNECTION_NOT_FOUND", "Provider connection not found", 404)
        return conn

    async def update_connection(
        self,
        connection_id: str,
        org_id: str,
        name: str | None = None,
        config: dict | None = None,
        credentials: dict[str, str] | None | object = _UNSET,
        status: str | None = None,
        updated_by: str | None = None,
    ) -> ProviderConnection:
        conn = await self.get_connection(connection_id, org_id)
        adapter = await self.db.get(ProviderAdapter, conn.adapter_id)
        cred_fields = set((adapter.credential_fields if adapter else []) or [])

        if name is not None:
            conn.name = name
        if config is not None:
            leaked = cred_fields & set(config.keys())
            if leaked:
                raise AppError(
                    "CREDENTIAL_IN_CONFIG",
                    f"Credential fields must not appear in config: {', '.join(sorted(leaked))}",
                    422,
                )
            conn.config = config
        if status is not None:
            conn.status = status
        if credentials is None:
            # Explicit null detaches the credential AND deletes the row —
            # it belongs to this connection (same ownership as delete_connection),
            # so leaving it orphaned would strand encrypted material.
            if conn.credential_id:
                cred = await self.db.get(OrgCredential, conn.credential_id)
                if cred is not None:
                    await self.db.delete(cred)
                conn.credential_id = None
        elif credentials is not _UNSET:
            if not credentials:
                raise AppError(
                    "EMPTY_CREDENTIALS",
                    "Credential dict must not be empty — send null to detach credentials",
                    422,
                )
            unknown = set(credentials.keys()) - cred_fields
            if unknown:
                raise AppError(
                    "UNKNOWN_CREDENTIAL_FIELD",
                    f"Adapter does not declare credential fields: {', '.join(sorted(unknown))}",
                    422,
                )
            if conn.credential_id:
                cred = await self.db.get(OrgCredential, conn.credential_id)
                if cred is not None:
                    cred.encrypted_data = encrypt_credentials(credentials)
                else:
                    conn.credential_id = None
            if not conn.credential_id:
                cred = OrgCredential(
                    org_id=org_id,
                    # Same truncation as create: String(100) column
                    name=f"{conn.name[:88]} credentials",
                    encrypted_data=encrypt_credentials(credentials),
                    created_by=updated_by,
                )
                self.db.add(cred)
                await self.db.flush()
                conn.credential_id = cred.id

        await self.db.flush()
        return conn

    async def delete_connection(self, connection_id: str, org_id: str) -> None:
        conn = await self.get_connection(connection_id, org_id)
        # Delete the credential too (not just orphan it)
        if conn.credential_id:
            cred = await self.db.get(OrgCredential, conn.credential_id)
            if cred is not None:
                await self.db.delete(cred)
        await self.db.delete(conn)
        await self.db.flush()
        log.info("provider_connection_deleted", connection_id=connection_id, org_id=org_id)

    # ── Offerings ─────────────────────────────────────────

    async def create_offering(
        self,
        org_id: str,
        connection_id: str,
        capability_key: str,
        model_name: str,
        features: list[str],
        limits: dict,
        cost_per_call_usd: float | None,
        quality_tier: str,
    ) -> ProviderModelOffering:
        await self.get_connection(connection_id, org_id)  # ownership check

        # Capability must exist in the taxonomy (closed vocabulary)
        cap = await self.get_capability(capability_key)
        if cap is None:
            raise AppError(
                "UNKNOWN_CAPABILITY",
                f"Capability '{capability_key}' is not in the taxonomy",
                422,
            )

        count_r = await self.db.execute(
            select(func.count()).where(ProviderModelOffering.connection_id == connection_id)
        )
        if count_r.scalar_one() >= MAX_OFFERINGS_PER_CONNECTION:
            raise AppError(
                "OFFERING_LIMIT_REACHED",
                f"Maximum {MAX_OFFERINGS_PER_CONNECTION} offerings per connection",
                422,
            )

        offering = ProviderModelOffering(
            connection_id=connection_id,
            capability_key=capability_key,
            model_name=model_name,
            features=features,
            limits=limits,
            cost_per_call_usd=cost_per_call_usd,
            quality_tier=quality_tier,
        )
        self.db.add(offering)
        await self.db.flush()
        return offering

    async def list_offerings(
        self, org_id: str, capability_key: str | None = None, active_only: bool = True
    ) -> list[ProviderModelOffering]:
        """List offerings across all of an org's connections."""
        query = (
            select(ProviderModelOffering)
            .join(ProviderConnection, ProviderConnection.id == ProviderModelOffering.connection_id)
            .where(ProviderConnection.org_id == org_id)
        )
        if active_only:
            query = query.where(
                ProviderModelOffering.is_active.is_(True),
                ProviderConnection.status == "active",
            )
        if capability_key:
            query = query.where(ProviderModelOffering.capability_key == capability_key)
        result = await self.db.execute(query.order_by(ProviderModelOffering.created_at))
        return list(result.scalars().all())

    async def get_offering(self, offering_id: str, org_id: str) -> ProviderModelOffering:
        offering = await self.db.get(ProviderModelOffering, offering_id)
        if offering is None:
            raise AppError("OFFERING_NOT_FOUND", "Provider offering not found", 404)
        conn = await self.db.get(ProviderConnection, offering.connection_id)
        if conn is None or conn.org_id != org_id:
            raise AppError("OFFERING_NOT_FOUND", "Provider offering not found", 404)
        return offering

    # Nullable offering columns where an explicit null means "clear the field".
    # Non-nullable columns (model_name, features, limits, quality_tier,
    # is_active) still ignore None — an explicit null there would 500 at flush.
    _NULLABLE_OFFERING_FIELDS = frozenset({"cost_per_call_usd"})

    async def update_offering(self, offering_id: str, org_id: str, **fields) -> ProviderModelOffering:
        offering = await self.get_offering(offering_id, org_id)
        for key, value in fields.items():
            if not hasattr(offering, key):
                continue
            # The endpoint dumps with exclude_unset, so a None here is an
            # EXPLICIT null from the client — clear nullable fields instead
            # of silently dropping the update.
            if value is not None or key in self._NULLABLE_OFFERING_FIELDS:
                setattr(offering, key, value)
        await self.db.flush()
        return offering

    async def delete_offering(self, offering_id: str, org_id: str) -> None:
        offering = await self.get_offering(offering_id, org_id)
        await self.db.delete(offering)
        await self.db.flush()

    # ── Capability satisfaction check (used by installer) ─

    async def check_capabilities(
        self, org_id: str, required: list[dict]
    ) -> list[dict]:
        """Check org's active offerings against required capabilities.

        Returns a list of gap dicts (empty = all satisfied). Each required
        entry: {"capability": str, "features": [str]}.

        Manifests are attacker-controlled (public packs), so entries are
        hardened here as defense in depth alongside the publish-time gate:
        a non-dict entry, non-string capability, or non-list features never
        raises — it becomes a MALFORMED_REQUIREMENT gap instead of a 500.
        """
        gaps: list[dict] = []
        # Normalize requirements before querying: (cap_key, features) tuples
        # plus a MALFORMED_REQUIREMENT gap for anything type-broken.
        normalized: list[tuple[str, set[str]]] = []
        for req in required:
            if not isinstance(req, dict):
                gaps.append(
                    {
                        "code": "MALFORMED_REQUIREMENT",
                        "capability": "",
                        "missing_features": [],
                        "detail": "Capability requirement entry is not an object",
                    }
                )
                continue
            cap_key = req.get("capability", "")
            if not isinstance(cap_key, str) or not cap_key:
                gaps.append(
                    {
                        "code": "MALFORMED_REQUIREMENT",
                        "capability": "",
                        "missing_features": [],
                        "detail": "Capability requirement has a non-string or empty 'capability'",
                    }
                )
                continue
            features = req.get("features", [])
            if not isinstance(features, list):
                # A string here would silently degrade to per-character subset
                # matching via set("highres") — treat as [] and flag instead.
                gaps.append(
                    {
                        "code": "MALFORMED_REQUIREMENT",
                        "capability": cap_key,
                        "missing_features": [],
                        "detail": f"'features' for '{cap_key}' is not a list; ignored",
                    }
                )
                features = []
            req_features = {f for f in features if isinstance(f, str)}
            normalized.append((cap_key, req_features))
        # One query for all requested capabilities (was N+1: one list_offerings
        # per requirement — up to MAX_DEPENDENCIES sequential SELECTs per install)
        cap_keys = {cap_key for cap_key, _ in normalized}
        offerings_by_cap: dict[str, list] = {k: [] for k in cap_keys}
        if cap_keys:
            result = await self.db.execute(
                select(ProviderModelOffering)
                .join(
                    ProviderConnection,
                    ProviderConnection.id == ProviderModelOffering.connection_id,
                )
                .where(
                    ProviderConnection.org_id == org_id,
                    ProviderConnection.status == "active",
                    ProviderModelOffering.is_active.is_(True),
                    ProviderModelOffering.capability_key.in_(cap_keys),
                )
            )
            for off in result.scalars().all():
                offerings_by_cap[off.capability_key].append(off)
        for cap_key, req_features in normalized:
            satisfied = any(
                req_features <= set(off.features or [])
                for off in offerings_by_cap.get(cap_key, [])
            )
            if not satisfied:
                gaps.append(
                    {
                        "code": "CAPABILITY_UNSATISFIED",
                        "capability": cap_key,
                        "missing_features": sorted(req_features),
                        "detail": (
                            f"No active provider offering for '{cap_key}'"
                            + (f" with features {sorted(req_features)}" if req_features else "")
                        ),
                    }
                )
        return gaps
