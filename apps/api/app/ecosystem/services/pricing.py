"""Pricing / limits / availability intelligence (ADR-016 Part E).

Observed external pricing NEVER becomes a billing cost rate directly: an
admin must reconcile-approve, which creates a NEW ProviderCostRate row in the
control-plane catalog (append-style, effective-dated). Rejection and
supersession are audit-tracked.
"""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.catalog import CATALOG_KIND_TO_MODEL
from app.ecosystem.models.mapping import (
    AVAILABILITY_RECORD_TYPES,
    PRICE_UNITS,
    AvailabilityRecord,
    PriceObservation,
)
from app.ecosystem.models.observation import EcosystemObservation
from app.exceptions import AppError

# Ecosystem price units → control-plane canonical usage units
_UNIT_TO_CP = {
    "token_input": ("llm_tokens_input", "token"),
    "token_output": ("llm_tokens_output", "token"),
    "image": ("image_generation", "image"),
    "megapixel": ("image_generation", "megapixel"),
    "video_second": ("video_generation", "second"),
    "minute": ("audio_generation", "minute"),
    "request": ("api_request", "request"),
    "subscription_month": ("subscription", "month"),
    "volume_tier": ("volume", "unit"),
}


class PricingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_from_observation(self, observation_id: str) -> list[PriceObservation]:
        """Materialize PriceObservation rows from a price-bearing observation."""
        obs = await self.db.get(EcosystemObservation, observation_id)
        if not obs:
            raise AppError("NOT_FOUND", "Observation not found", 404)
        if obs.canonical_entity_id is None:
            raise AppError(
                "ECO_MERGE_CONFIRMATION_REQUIRED",
                "Observation must be resolved to a canonical entity first",
                409,
            )
        norm = obs.normalized or {}
        prices = norm.get("pricing") or (
            [norm] if norm.get("price") is not None and norm.get("unit") else []
        )
        created: list[PriceObservation] = []
        for p in prices:
            if not isinstance(p, dict):
                continue
            unit = p.get("unit")
            if unit not in PRICE_UNITS:
                continue
            try:
                price = Decimal(str(p.get("price")))
            except (InvalidOperation, TypeError):
                continue
            if price < 0 or price > Decimal("1e9"):
                continue
            row = PriceObservation(
                observation_id=obs.id,
                entity_kind=obs.canonical_entity_kind,
                entity_id=obs.canonical_entity_id,
                region=p.get("region"),
                unit=unit,
                price=price,
                currency=(p.get("currency") or "USD")[:3].upper(),
                tier=p.get("tier") if isinstance(p.get("tier"), dict) else None,
                effective_at=obs.effective_at,
                observed_at=obs.observed_at,
            )
            self.db.add(row)
            created.append(row)
        await self.db.flush()
        return created

    async def list(
        self,
        *,
        entity_kind: str | None = None,
        entity_id: str | None = None,
        reconciliation_status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[PriceObservation]:
        query = select(PriceObservation)
        if entity_kind:
            query = query.where(PriceObservation.entity_kind == entity_kind)
        if entity_id:
            query = query.where(PriceObservation.entity_id == entity_id)
        if reconciliation_status:
            query = query.where(
                PriceObservation.reconciliation_status == reconciliation_status
            )
        rows = await self.db.scalars(
            query.order_by(PriceObservation.observed_at.desc()).limit(limit).offset(offset)
        )
        return list(rows)

    async def reconcile(
        self,
        price_obs_id: str,
        *,
        decision: str,
        actor_id: str,
        provider_key: str | None = None,
        model_or_service: str | None = None,
    ) -> PriceObservation:
        """Approve/reject an observed price. Approval mints a NEW cost rate.

        The billing catalog is never mutated in place and never auto-approved
        (ECO_PRICING_NOT_APPROVED protects any downstream shortcut).
        """
        row = await self.db.get(PriceObservation, price_obs_id)
        if not row:
            raise AppError("NOT_FOUND", "Price observation not found", 404)
        if row.reconciliation_status in ("approved", "rejected", "superseded"):
            raise AppError("ECO_INVALID_TRANSITION", "Price observation already decided", 409)
        if decision == "under_review":
            row.reconciliation_status = "under_review"
            await self.db.flush()
            return row
        if decision == "reject":
            row.reconciliation_status = "rejected"
            row.reconciled_by = actor_id
            row.reconciled_at = datetime.now(UTC)
            await self.db.flush()
            return row
        if decision != "approve":
            raise AppError("VALIDATION_ERROR", f"Unknown decision: {decision}", 422)
        if not provider_key:
            raise AppError(
                "VALIDATION_ERROR", "provider_key required to approve into billing", 422
            )

        # Mint the approved rate in the control-plane catalog (new row,
        # effective from now — historical rated usage is untouched).
        from app.controlplane.models.pricing import ProviderCostRate

        usage_type, cp_unit = _UNIT_TO_CP.get(row.unit, ("api_request", "request"))
        rate = ProviderCostRate(
            provider=provider_key,
            model_or_service=model_or_service,
            usage_type=usage_type,
            unit=cp_unit,
            currency=row.currency,
            unit_cost=row.price,
            effective_from=datetime.now(UTC),
            source_note=f"eco:price_observation:{row.id}",
            created_by=actor_id,
        )
        self.db.add(rate)
        await self.db.flush()
        row.reconciliation_status = "approved"
        row.reconciled_by = actor_id
        row.reconciled_at = datetime.now(UTC)
        row.approved_cost_rate_id = rate.id
        # Supersede older approved observations for the same key
        older = await self.db.scalars(
            select(PriceObservation).where(
                PriceObservation.entity_kind == row.entity_kind,
                PriceObservation.entity_id == row.entity_id,
                PriceObservation.unit == row.unit,
                PriceObservation.region.is_(row.region) if row.region is None
                else PriceObservation.region == row.region,
                PriceObservation.reconciliation_status == "approved",
                PriceObservation.id != row.id,
            )
        )
        for old in older:
            old.reconciliation_status = "superseded"
        await self.db.flush()
        return row


async def _mock_prober(entity_kind: str, entity_id: str) -> dict:
    """Default availability prober — deterministic mock; provider adapters can
    replace it via set_availability_prober() (ADR-016 §11.3)."""
    return {"status": "operational", "probe": {"kind": "mock"}}


# Injectable module-level prober so worker + tests share one seam
AVAILABILITY_PROBER = _mock_prober


def set_availability_prober(prober) -> None:
    global AVAILABILITY_PROBER
    AVAILABILITY_PROBER = prober


class AvailabilityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def probe_status(self, entity_kind: str, entity_id: str) -> AvailabilityRecord:
        """§11.3: catalog presence ≠ availability — status is probed
        INDEPENDENTLY of catalog syncs and appended even when unchanged."""
        if entity_kind not in CATALOG_KIND_TO_MODEL:
            raise AppError("VALIDATION_ERROR", f"Unknown entity kind: {entity_kind}", 422)
        if await self.db.get(CATALOG_KIND_TO_MODEL[entity_kind], entity_id) is None:
            raise AppError("NOT_FOUND", "Entity not found", 404)
        try:
            result = await AVAILABILITY_PROBER(entity_kind, entity_id)
            status = result.get("status", "unreachable")
            if status not in ("operational", "degraded", "unreachable"):
                status = "unreachable"
            value = {"status": status, "probe": result.get("probe", {})}
        except Exception as exc:  # noqa: BLE001 — a failing probe IS the signal
            value = {"status": "unreachable", "probe": {"error": str(exc)[:200]}}
        # §14 early warning (StatusGator): a status FLIP is itself an event —
        # compare with the previous probe before appending the new record
        previous = await self.db.scalar(
            select(AvailabilityRecord)
            .where(
                AvailabilityRecord.entity_kind == entity_kind,
                AvailabilityRecord.entity_id == entity_id,
                AvailabilityRecord.record_type == "status",
            )
            .order_by(AvailabilityRecord.observed_at.desc(), AvailabilityRecord.id.desc())
            .limit(1)
        )
        record = await self.record(
            entity_kind=entity_kind,
            entity_id=entity_id,
            record_type="status",
            value=value,
        )
        prev_status = (previous.value or {}).get("status") if previous else None
        if prev_status and prev_status != value["status"]:
            await self._emit_status_flip(entity_kind, entity_id, prev_status, value["status"])
        return record

    async def _emit_status_flip(
        self, entity_kind: str, entity_id: str, old_status: str, new_status: str
    ) -> None:
        """Availability flip → typed change event on the internal probe source
        (rides the normal fan-out: watcher notifications, webhooks)."""
        import hashlib
        from datetime import UTC, datetime

        from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation
        from app.ecosystem.models.source import EcosystemSource
        from app.ecosystem.services.change_detection import _fanout

        source = await self.db.scalar(
            select(EcosystemSource).where(
                EcosystemSource.name == "internal:availability-probes"
            )
        )
        if source is None:
            source = EcosystemSource(
                name="internal:availability-probes",
                source_type="internal_research",
                trust_level="internal",
                adapter_key="manual",
                parser_version="1.0",
                robots_compliant=True,
            )
            self.db.add(source)
            await self.db.flush()
        raw = f"{entity_kind}:{entity_id}:{old_status}->{new_status}:{datetime.now(UTC).isoformat()}"
        obs = EcosystemObservation(
            source_id=source.id,
            event_type="availability_changed",
            entity_kind=entity_kind,
            canonical_entity_kind=entity_kind,
            canonical_entity_id=entity_id,
            raw_hash=hashlib.sha256(raw.encode()).hexdigest(),
            normalized={"old_status": old_status, "new_status": new_status},
            extraction_method="structured",
        )
        self.db.add(obs)
        await self.db.flush()
        degraded = new_status in ("degraded", "unreachable")
        change = ChangeEvent(
            observation_id=obs.id,
            change_type="region",
            field="availability_status",
            old_value={"value": old_status},
            new_value={"value": new_status},
            severity="degraded" if degraded else "info",
            entity_kind=entity_kind,
            canonical_entity_id=entity_id,
        )
        self.db.add(change)
        await self.db.flush()
        _fanout(self.db, change)
        await self.db.flush()

    async def record(
        self,
        *,
        entity_kind: str,
        entity_id: str,
        record_type: str,
        value: dict,
        region: str | None = None,
        source_observation_id: str | None = None,
    ) -> AvailabilityRecord:
        if record_type not in AVAILABILITY_RECORD_TYPES:
            raise AppError("VALIDATION_ERROR", f"Unknown record type: {record_type}", 422)
        row = AvailabilityRecord(
            entity_kind=entity_kind,
            entity_id=entity_id,
            record_type=record_type,
            value=value,
            region=region,
            source_observation_id=source_observation_id,
        )
        self.db.add(row)
        await self.db.flush()
        return row

    async def list(
        self,
        *,
        entity_kind: str | None = None,
        entity_id: str | None = None,
        record_type: str | None = None,
        limit: int = 100,
    ) -> list[AvailabilityRecord]:
        query = select(AvailabilityRecord)
        if entity_kind:
            query = query.where(AvailabilityRecord.entity_kind == entity_kind)
        if entity_id:
            query = query.where(AvailabilityRecord.entity_id == entity_id)
        if record_type:
            query = query.where(AvailabilityRecord.record_type == record_type)
        rows = await self.db.scalars(
            query.order_by(AvailabilityRecord.observed_at.desc()).limit(limit)
        )
        return list(rows)
