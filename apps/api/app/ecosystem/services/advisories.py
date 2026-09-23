"""Security advisory registry + affected-entity resolution (ADR-016 §38).

Snyk/Dependabot bar: a structured advisory (ref, severity, name + version
range) instead of loose change events. Registration emits ONE
security_critical/breaking change event on the internal security source so
the normal fan-out (watchers, webhooks, Atom, delta export) carries it.
Never auto-blocks or auto-migrates anything — lifecycle stays human.
"""

import hashlib
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.advisory import (
    ADVISORY_SEVERITIES,
    ADVISORY_STATUSES,
    SecurityAdvisory,
)
from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL, ModelVersion
from app.ecosystem.security import escape_like, sanitize_text
from app.ecosystem.services.stats import version_in_range
from app.exceptions import AppError

_CHANGE_SEVERITY = {"critical": "security_critical", "high": "security_critical"}


class AdvisoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        advisory_ref: str,
        title: str,
        severity: str,
        affected_ref: str,
        affected_kind: str | None = None,
        affected_range: str | None = None,
        fixed_in: str | None = None,
        description: str | None = None,
        source_observation_id: str | None = None,
        created_by: str,
    ) -> SecurityAdvisory:
        if severity not in ADVISORY_SEVERITIES:
            raise AppError("VALIDATION_ERROR", f"Unknown severity: {severity}", 422)
        if affected_kind is not None and affected_kind not in CATALOG_KIND_TO_MODEL:
            raise AppError("VALIDATION_ERROR", f"Unknown entity kind: {affected_kind}", 422)
        ref = sanitize_text(advisory_ref, 100)
        if not ref:
            raise AppError("VALIDATION_ERROR", "advisory_ref required", 422)
        if await self.db.scalar(
            select(SecurityAdvisory.id).where(SecurityAdvisory.advisory_ref == ref)
        ):
            raise AppError("ECO_ADVISORY_EXISTS", "Advisory ref already registered", 409)
        advisory = SecurityAdvisory(
            advisory_ref=ref,
            title=sanitize_text(title, 300) or ref,
            severity=severity,
            description=sanitize_text(description, 5000),
            affected_kind=affected_kind,
            affected_ref=sanitize_text(affected_ref, 300) or "",
            affected_range=sanitize_text(affected_range, 100),
            fixed_in=sanitize_text(fixed_in, 50),
            source_observation_id=source_observation_id,
            created_by=created_by,
        )
        if not advisory.affected_ref:
            raise AppError("VALIDATION_ERROR", "affected_ref required", 422)
        self.db.add(advisory)
        await self.db.flush()
        await self._emit_change(advisory)
        await self._notify_affected(advisory)
        return advisory

    async def _notify_affected(self, advisory: SecurityAdvisory) -> None:
        """Per-affected-entity change events (capped) so WATCHERS of a hit
        entity are notified — 'a model I watch has a CVE' is the whole point.
        Rides the same fan-out; the registry-level event already exists, these
        carry canonical_entity_id for watchlist matching."""
        from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation

        affected = await self.affected_entities(advisory.id, limit=50)
        if not affected:
            return
        obs = await self.db.scalar(
            select(EcosystemObservation)
            .where(EcosystemObservation.raw_hash == hashlib.sha256(
                f"advisory:{advisory.advisory_ref}".encode()
            ).hexdigest())
            .limit(1)
        )
        if obs is None:
            return
        from app.ecosystem.services.change_detection import _fanout

        severity = _CHANGE_SEVERITY.get(advisory.severity, "breaking")
        for hit in affected:
            change = ChangeEvent(
                observation_id=obs.id,
                change_type="security",
                field="security_advisory_affects",
                old_value=None,
                new_value={
                    "advisory_ref": advisory.advisory_ref,
                    "severity": advisory.severity,
                    "range_match": hit["range_match"],
                    "fixed_in": advisory.fixed_in,
                },
                severity=severity,
                entity_kind=hit["entity_kind"],
                canonical_entity_id=hit["entity_id"],
            )
            self.db.add(change)
            await self.db.flush()
            _fanout(self.db, change)
        await self.db.flush()

    async def _emit_change(self, advisory: SecurityAdvisory) -> None:
        """One typed change event per registration — rides normal fan-out."""
        from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
        from app.ecosystem.models.source import EcosystemSource
        from app.ecosystem.services.change_detection import _fanout

        source = await self.db.scalar(
            select(EcosystemSource).where(EcosystemSource.name == "internal:security-desk")
        )
        if source is None:
            source = EcosystemSource(
                name="internal:security-desk",
                source_type="internal_research",
                trust_level="internal",
                adapter_key="manual",
                parser_version="1.0",
                robots_compliant=True,
            )
            self.db.add(source)
            await self.db.flush()
        obs = EcosystemObservation(
            source_id=source.id,
            event_type="security_advisory",
            entity_kind=advisory.affected_kind,
            raw_hash=hashlib.sha256(f"advisory:{advisory.advisory_ref}".encode()).hexdigest(),
            normalized={
                "advisory_ref": advisory.advisory_ref,
                "severity": advisory.severity,
                "affected_ref": advisory.affected_ref,
                "affected_range": advisory.affected_range,
                "fixed_in": advisory.fixed_in,
            },
            extraction_method="structured",
            human_verified=True,  # registration IS the human verification
        )
        self.db.add(obs)
        await self.db.flush()
        change = ChangeEvent(
            observation_id=obs.id,
            change_type="security",
            field="security_advisory",
            old_value=None,
            new_value={
                "advisory_ref": advisory.advisory_ref,
                "severity": advisory.severity,
                "affected_ref": advisory.affected_ref,
            },
            severity=_CHANGE_SEVERITY.get(advisory.severity, "breaking"),
            entity_kind=advisory.affected_kind,
        )
        self.db.add(change)
        await self.db.flush()
        _fanout(self.db, change)
        await self.db.flush()

    async def get(self, advisory_id: str) -> SecurityAdvisory:
        advisory = await self.db.get(SecurityAdvisory, advisory_id)
        if advisory is None:
            raise AppError("NOT_FOUND", "Advisory not found", 404)
        return advisory

    async def list(
        self, *, status: str | None = None, severity: str | None = None, limit: int = 50
    ) -> list[SecurityAdvisory]:
        query = select(SecurityAdvisory)
        if status:
            query = query.where(SecurityAdvisory.status == status)
        if severity:
            query = query.where(SecurityAdvisory.severity == severity)
        rows = await self.db.scalars(
            query.order_by(SecurityAdvisory.created_at.desc()).limit(limit)
        )
        return list(rows)

    async def transition(
        self, advisory_id: str, *, to_status: str, actor_id: str
    ) -> SecurityAdvisory:
        if to_status not in ADVISORY_STATUSES:
            raise AppError("VALIDATION_ERROR", f"Unknown status: {to_status}", 422)
        advisory = await self.get(advisory_id)
        advisory.status = to_status
        advisory.updated_at = datetime.now(UTC)
        await self.db.flush()
        return advisory

    async def affected_entities(self, advisory_id: str, *, limit: int = 100) -> "list[dict]":
        """Resolve which catalog entities the advisory touches.

        Name match on canonical_name (case-insensitive substring both ways is
        too loose — exact-insensitive or alias hit) and, for versioned kinds,
        version_in_range with FAIL-OPEN semantics: an unparseable range still
        counts as affected (unknown never means safe)."""
        advisory = await self.get(advisory_id)
        kinds = (
            [advisory.affected_kind]
            if advisory.affected_kind
            else list(CATALOG_KIND_TO_MODEL)
        )
        ref_lower = advisory.affected_ref.lower()
        out: list[dict] = []
        for kind in kinds:
            model = CATALOG_KIND_TO_MODEL[kind]
            # SQL-side prefilter: name prefix match OR alias containment —
            # never a full-table scan; matching semantics unchanged
            from sqlalchemy import Text as _Text
            from sqlalchemy import cast, func, or_

            rows = await self.db.scalars(
                select(model)
                .where(
                    or_(
                        func.lower(model.canonical_name).like(
                            f"{escape_like(ref_lower)}%", escape="\\"
                        ),
                        func.lower(cast(model.aliases, _Text)).like(
                            f"%{escape_like(ref_lower)}%", escape="\\"
                        ),
                    )
                )
                .limit(2000)
            )
            for entity in rows:
                name_hit = entity.canonical_name.lower() == ref_lower or ref_lower in [
                    str(a).lower() for a in (entity.aliases or [])
                ]
                if not name_hit and isinstance(entity, ModelVersion):
                    # model versions carry the model's name + their version
                    name_hit = entity.canonical_name.lower().startswith(ref_lower)
                if not name_hit:
                    continue
                version = getattr(entity, "version", None)
                in_range: bool | None = True
                if advisory.affected_range and version:
                    in_range = version_in_range(str(version), advisory.affected_range)
                if in_range is False:
                    continue  # provably outside the range
                out.append(
                    {
                        "entity_kind": kind,
                        "entity_id": entity.id,
                        "canonical_name": entity.canonical_name,
                        "version": version,
                        "range_match": (
                            "confirmed" if in_range is True and advisory.affected_range
                            else "unknown_fail_open" if in_range is None
                            else "name_only"
                        ),
                        "lifecycle_status": entity.lifecycle_status,
                    }
                )
                if len(out) >= limit:
                    return out
        return out
