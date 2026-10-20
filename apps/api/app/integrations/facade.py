"""Integration fabric facade (ADR-018 §3).

The ONLY surface other packages may import from app.integrations.
Kept deliberately thin in P1; the event-mesh emit API lands in P2.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


async def sync_provider_catalog(db: AsyncSession) -> int:
    """Upsert the in-repo provider catalog (idempotent; startup/admin use)."""
    from app.integrations.services.connections import ConnectionService

    return await ConnectionService(db).sync_provider_catalog()


async def emit_event(
    db: AsyncSession,
    org_id: str,
    event_type: str,
    *,
    subject: str | None = None,
    data: dict | None = None,
    version: int = 1,
):
    """Append a canonical mesh event (CloudEvents) + its outbox message in
    the CALLER's transaction (ADR-018 §12.1). ``event_type`` is the bare
    catalog name, e.g. "project.approved" → com.openskill.project.approved.v1.
    Delivery fan-out happens asynchronously in the outbox worker."""
    from app.integrations.services.events import emit_event as _emit

    return await _emit(db, org_id, event_type, subject=subject, data=data, version=version)


async def record_fabric_audit(
    db,
    org_id: str,
    actor_user_id: str | None,
    action: str,
    target_type: str,
    target_id: str,
    after: dict | None = None,
    *,
    system_actor: bool = False,
) -> None:
    """Issue #43 Part O: admin mutations on fabric config write the
    append-only audit trail. Best-effort — an audit hiccup never fails the
    operation; payloads carry config shape, NEVER secrets.

    R592: a human admin action passes actor_user_id and is recorded as a
    'tenant' actor. An IdP-driven action (SCIM deprovision) has NO human
    actor — pass system_actor=True so the deprovision is still recorded (as
    a 'system' actor) instead of silently dropped. Without a user id AND
    without system_actor, the call is a no-op (back-compat)."""
    if actor_user_id is None and not system_actor:
        return
    try:
        from app.controlplane import facade as cp_facade
        from app.controlplane.services.audit import Actor, record_audit

        actor = (
            Actor(user_id=None, type="system")
            if actor_user_id is None
            else Actor(user_id=actor_user_id, type="tenant")
        )
        tenant = await cp_facade.get_tenant_for_org(db, org_id)
        await record_audit(
            db,
            actor=actor,
            action=action,
            target_type=target_type,
            target_id=target_id,
            tenant_id=tenant.id,
            after=after or {},
        )
    except Exception:  # noqa: BLE001
        import structlog

        structlog.get_logger().warning(
            "fabric_audit_write_failed", action=action, target_id=target_id
        )
