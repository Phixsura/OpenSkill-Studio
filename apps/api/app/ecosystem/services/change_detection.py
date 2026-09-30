"""Structured change detection (ADR-016 Part B).

Compares a new observation's normalized payload against the most recent prior
observation for the same (source, external_ref) and emits TYPED ChangeEvent
rows — price, limits, license, api, model_version, lifecycle, region,
security — never plain text diffs.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ecosystem.models.observation import ChangeEvent, EcosystemObservation

# normalized field → (change_type, severity)
_TRACKED_FIELDS: dict[str, tuple[str, str]] = {
    "license": ("license", "breaking"),
    "limits": ("limits", "update_available"),
    "api_identifier": ("api", "update_available"),
    "version": ("model_version", "update_available"),
    "sunset_at": ("lifecycle", "sunset_risk"),
    "deprecated_at": ("lifecycle", "sunset_risk"),
    "regions": ("region", "info"),
    "pricing": ("price", "info"),
}

_EVENT_TYPE_SEVERITY = {
    "security_advisory": "security_critical",
    "model_deprecated": "sunset_risk",
}


def _wrap(value) -> dict | None:
    """JSONB columns need dict payloads; wrap scalars for storage."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    return {"value": value}


async def detect_changes(db: AsyncSession, obs: EcosystemObservation) -> int:
    """Emit typed change events for one freshly ingested observation."""
    created = 0
    events: list[ChangeEvent] = []

    # Event-type driven changes need no prior row (advisories, deprecations)
    if obs.event_type in _EVENT_TYPE_SEVERITY:
        event = ChangeEvent(
            observation_id=obs.id,
            change_type="security" if obs.event_type == "security_advisory" else "lifecycle",
            field=obs.event_type,
            old_value=None,
            new_value=_wrap(obs.normalized),
            severity=_EVENT_TYPE_SEVERITY[obs.event_type],
            entity_kind=obs.entity_kind,
            canonical_entity_id=obs.canonical_entity_id,
        )
        db.add(event)
        events.append(event)
        created += 1

    if not obs.external_ref:
        await db.flush()
        for event in events:
            _fanout(db, event)
        await db.flush()
        return created

    prior = await db.scalar(
        select(EcosystemObservation)
        .where(
            EcosystemObservation.source_id == obs.source_id,
            EcosystemObservation.external_ref == obs.external_ref,
            EcosystemObservation.id != obs.id,
            EcosystemObservation.superseded_by_id.is_(None),
        )
        .order_by(EcosystemObservation.observed_at.desc(), EcosystemObservation.id.desc())
        .limit(1)
    )
    if prior is None:
        await db.flush()
        for event in events:
            _fanout(db, event)
        await db.flush()
        return created

    old_norm = prior.normalized or {}
    new_norm = obs.normalized or {}
    for field, (change_type, severity) in _TRACKED_FIELDS.items():
        old_val = old_norm.get(field)
        new_val = new_norm.get(field)
        if old_val == new_val:
            continue
        if old_val is None and new_val is None:
            continue
        # Escalate price severity when a numeric increase is detectable and
        # carry the change magnitude in the typed payload
        eff_severity = severity
        wrapped_new = _wrap(new_val)
        if change_type == "price":
            eff_severity = _price_severity(old_val, new_val)
            magnitude = _price_magnitude(old_val, new_val)
            if magnitude is not None and isinstance(wrapped_new, dict):
                wrapped_new = {**wrapped_new, "magnitude": magnitude}
        event = ChangeEvent(
            observation_id=obs.id,
            change_type=change_type,
            field=field,
            old_value=_wrap(old_val),
            new_value=wrapped_new,
            severity=eff_severity,
            entity_kind=obs.entity_kind,
            canonical_entity_id=obs.canonical_entity_id or prior.canonical_entity_id,
        )
        db.add(event)
        events.append(event)
        created += 1
    await db.flush()
    for event in events:
        _fanout(db, event)
    await db.flush()
    return created


def _price_severity(old_val, new_val) -> str:
    """Price increases are update_available; decreases informational."""
    try:
        old_prices = {(p["unit"], p.get("region")): float(p["price"]) for p in old_val or []}
        new_prices = {(p["unit"], p.get("region")): float(p["price"]) for p in new_val or []}
    except (TypeError, KeyError, ValueError):
        return "info"
    for key, new_price in new_prices.items():
        old_price = old_prices.get(key)
        if old_price is not None and new_price > old_price:
            return "update_available"
    return "info"


def _price_magnitude(old_val, new_val) -> dict | None:
    """Max per-unit percentage change — Dependabot-grade typed payloads carry
    magnitude, not just before/after blobs."""
    try:
        old_prices = {(p["unit"], p.get("region")): float(p["price"]) for p in old_val or []}
        new_prices = {(p["unit"], p.get("region")): float(p["price"]) for p in new_val or []}
    except (TypeError, KeyError, ValueError):
        return None
    worst: dict | None = None
    for key, new_price in new_prices.items():
        old_price = old_prices.get(key)
        if old_price is None or old_price <= 0:
            continue
        pct = round((new_price - old_price) / old_price * 100, 2)
        if worst is None or abs(pct) > abs(worst["change_pct"]):
            worst = {"unit": key[0], "region": key[1], "change_pct": pct}
    return worst


# Severities that fan out automatically: impact analysis is enqueued and
# watchers are notified without an operator having to click anything
# (Dependabot lesson: new advisory → rescan all dependents, always).
AUTO_FANOUT_SEVERITIES = frozenset({"breaking", "security_critical", "sunset_risk"})


def _fanout(db, change: ChangeEvent) -> None:
    """Enqueue impact computation + watcher notification for one change.

    Same-transaction outbox rows (ADR-014): a committed change event always
    has its fan-out messages; the worker dedupes (impact is idempotent per
    change event, notifications idempotent per (watcher, change))."""
    from app.controlplane.models.outbox import enqueue

    if change.canonical_entity_id and change.severity in AUTO_FANOUT_SEVERITIES:
        enqueue(db, "eco.compute_impact", {"change_event_id": change.id})
    if change.canonical_entity_id:
        enqueue(db, "eco.notify_watchers", {"change_event_id": change.id})
