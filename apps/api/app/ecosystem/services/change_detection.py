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

    # Event-type driven changes need no prior row (advisories, deprecations)
    if obs.event_type in _EVENT_TYPE_SEVERITY:
        db.add(
            ChangeEvent(
                observation_id=obs.id,
                change_type="security" if obs.event_type == "security_advisory" else "lifecycle",
                field=obs.event_type,
                old_value=None,
                new_value=_wrap(obs.normalized),
                severity=_EVENT_TYPE_SEVERITY[obs.event_type],
                entity_kind=obs.entity_kind,
                canonical_entity_id=obs.canonical_entity_id,
            )
        )
        created += 1

    if not obs.external_ref:
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
        # Escalate price severity when a numeric increase is detectable
        eff_severity = severity
        if change_type == "price":
            eff_severity = _price_severity(old_val, new_val)
        db.add(
            ChangeEvent(
                observation_id=obs.id,
                change_type=change_type,
                field=field,
                old_value=_wrap(old_val),
                new_value=_wrap(new_val),
                severity=eff_severity,
                entity_kind=obs.entity_kind,
                canonical_entity_id=obs.canonical_entity_id or prior.canonical_entity_id,
            )
        )
        created += 1
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
