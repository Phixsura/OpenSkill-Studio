"""Pricing / limits / availability intelligence (ADR-016 Part E).

Observed external pricing NEVER becomes a billing cost rate directly: an
admin must reconcile-approve, which creates a NEW ProviderCostRate row in the
control-plane catalog (append-style, effective-dated). Rejection and
supersession are audit-tracked.
"""

from datetime import UTC, datetime, timedelta
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

    async def latest_prices(self, entity_kind: str, entity_id: str) -> dict[str, dict]:
        """Latest price per unit for one entity — approved rows win over
        merely-observed ones; within a class, most recently observed wins."""
        rows = await self.db.scalars(
            select(PriceObservation)
            .where(
                PriceObservation.entity_kind == entity_kind,
                PriceObservation.entity_id == entity_id,
                PriceObservation.reconciliation_status.notin_(("rejected", "superseded")),
            )
            .order_by(PriceObservation.observed_at.desc())
            .limit(200)
        )
        best: dict[str, dict] = {}
        for row in rows:
            current = best.get(row.unit)
            candidate = {
                "unit": row.unit,
                "price": float(row.price),
                "currency": row.currency,
                "region": row.region,
                "approved": row.reconciliation_status == "approved",
                "observed_at": row.observed_at.isoformat() if row.observed_at else None,
            }
            if current is None or (candidate["approved"] and not current["approved"]):
                best[row.unit] = candidate
        return best

    async def history(
        self, *, entity_kind: str, entity_id: str, unit: str | None = None
    ) -> dict:
        """AA price-over-time bar: per-unit time series of non-rejected price
        observations (oldest first) + linear trend per unit (slope in
        price/day, projected next). Projection is advisory, never a rate."""
        from app.ecosystem.services.stats import linear_trend

        query = (
            select(PriceObservation)
            .where(
                PriceObservation.entity_kind == entity_kind,
                PriceObservation.entity_id == entity_id,
                PriceObservation.reconciliation_status.notin_(("rejected", "superseded")),
            )
            .order_by(PriceObservation.observed_at.asc())
            .limit(500)
        )
        if unit:
            if unit not in PRICE_UNITS:
                raise AppError("VALIDATION_ERROR", f"Unknown price unit: {unit}", 422)
            query = query.where(PriceObservation.unit == unit)
        rows = list(await self.db.scalars(query))
        series: dict[str, list[dict]] = {}
        for row in rows:
            series.setdefault(row.unit, []).append(
                {
                    "price": float(row.price),
                    "currency": row.currency,
                    "observed_at": row.observed_at.isoformat() if row.observed_at else None,
                    "approved": row.reconciliation_status == "approved",
                }
            )
        trends: dict[str, dict | None] = {}
        for u, points in series.items():
            usable = [
                p2 for p2 in points if p2["observed_at"] is not None
            ]
            if len(usable) >= 2:
                base = datetime.fromisoformat(usable[0]["observed_at"])
                xy = [
                    (
                        (datetime.fromisoformat(p2["observed_at"]) - base).total_seconds()
                        / 86400.0,
                        p2["price"],
                    )
                    for p2 in usable
                ]
                trends[u] = linear_trend(xy)
            else:
                trends[u] = None
        return {
            "entity_kind": entity_kind,
            "entity_id": entity_id,
            "series": series,
            "trends": trends,
        }

    async def estimate(
        self,
        *,
        entity_kind: str,
        entity_ids: "list[str]",
        workload: "dict[str, float]",
    ) -> "list[dict]":
        """OpenRouter-style workload cost estimator: given unit quantities
        (e.g. {"token_input": 1e6, "token_output": 2e5}), price the workload
        against each entity's latest observed/approved prices. NEVER a quote —
        estimates are advisory and flag any unpriced unit explicitly."""
        if not workload:
            raise AppError("VALIDATION_ERROR", "workload must not be empty", 422)
        if len(entity_ids) > 20:
            raise AppError("VALIDATION_ERROR", "At most 20 entities per estimate", 422)
        for unit, qty in workload.items():
            if unit not in PRICE_UNITS:
                raise AppError("VALIDATION_ERROR", f"Unknown price unit: {unit}", 422)
            try:
                qty_f = float(qty)
            except (TypeError, ValueError):
                raise AppError("VALIDATION_ERROR", f"Invalid quantity for {unit}", 422) from None
            if not (0 <= qty_f <= 1e12):
                raise AppError("VALIDATION_ERROR", f"Quantity out of range for {unit}", 422)
        results = []
        for entity_id in entity_ids:
            prices = await self.latest_prices(entity_kind, entity_id)
            breakdown = []
            total = 0.0
            missing = []
            all_approved = True
            for unit, qty in workload.items():
                price = prices.get(unit)
                if price is None:
                    missing.append(unit)
                    continue
                line = round(float(qty) * price["price"], 6)
                total += line
                all_approved = all_approved and price["approved"]
                breakdown.append(
                    {
                        "unit": unit,
                        "quantity": float(qty),
                        "unit_price": price["price"],
                        "currency": price["currency"],
                        "approved": price["approved"],
                        "line_total": line,
                    }
                )
            results.append(
                {
                    "entity_kind": entity_kind,
                    "entity_id": entity_id,
                    "estimated_total": round(total, 6) if breakdown else None,
                    "currency": breakdown[0]["currency"] if breakdown else None,
                    "breakdown": breakdown,
                    "missing_units": missing,
                    "fully_priced": not missing,
                    "all_prices_approved": bool(breakdown) and all_approved,
                }
            )
        # Fully-priced first, then cheapest
        results.sort(
            key=lambda r: (not r["fully_priced"], r["estimated_total"] if r["estimated_total"] is not None else float("inf"))
        )
        return results

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

    async def uptime(
        self, *, entity_kind: str, entity_id: str, days: int = 30
    ) -> dict:
        """StatusGator-style SLO summary over trailing `days`: time-weighted
        uptime %, incident count, current status, per-day worst status. Built
        purely from our own probe history — honest 'unknown' before the first
        probe rather than assumed-up."""
        if not (1 <= days <= 365):
            raise AppError("VALIDATION_ERROR", "days must be 1-365", 422)
        window_start = datetime.now(UTC) - timedelta(days=days)
        rows = list(
            await self.db.scalars(
                select(AvailabilityRecord)
                .where(
                    AvailabilityRecord.entity_kind == entity_kind,
                    AvailabilityRecord.entity_id == entity_id,
                    AvailabilityRecord.record_type == "status",
                )
                .order_by(AvailabilityRecord.observed_at.asc())
            )
        )
        now = datetime.now(UTC)
        # Status intervals: each probe's status holds until the next probe
        points = [
            ((r.observed_at if r.observed_at.tzinfo else r.observed_at.replace(tzinfo=UTC)),
             (r.value or {}).get("status") or "unknown")
            for r in rows
        ]
        up_seconds = 0.0
        down_seconds = 0.0
        incidents = 0
        prev_status: str | None = None
        day_worst: dict[str, str] = {}
        rank = {"operational": 0, "unknown": 1, "degraded": 2, "unreachable": 3}
        for i, (ts, status) in enumerate(points):
            end = points[i + 1][0] if i + 1 < len(points) else now
            seg_start = max(ts, window_start)
            seg_end = max(min(end, now), seg_start)
            span = (seg_end - seg_start).total_seconds()
            if span > 0:
                if status == "operational":
                    up_seconds += span
                elif status in ("degraded", "unreachable"):
                    down_seconds += span
            if prev_status not in (None, "degraded", "unreachable") and status in (
                "degraded",
                "unreachable",
            ):
                incidents += 1
            prev_status = status
            # Per-day worst status (only days the interval touches, within window)
            cursor = seg_start
            while cursor < seg_end:
                key = cursor.date().isoformat()
                if rank.get(status, 1) > rank.get(day_worst.get(key, "operational"), 0):
                    day_worst[key] = status
                cursor = datetime(
                    cursor.year, cursor.month, cursor.day, tzinfo=UTC
                ) + timedelta(days=1)
        observed = up_seconds + down_seconds
        return {
            "entity_kind": entity_kind,
            "entity_id": entity_id,
            "window_days": days,
            "current_status": points[-1][1] if points else "unknown",
            "uptime_pct": round(100.0 * up_seconds / observed, 3) if observed > 0 else None,
            "observed_seconds": round(observed, 1),
            "coverage_pct": round(100.0 * observed / (days * 86400), 3),
            "incidents": incidents,
            "daily": [
                {"date": d, "worst_status": day_worst[d]} for d in sorted(day_worst)
            ],
        }

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
