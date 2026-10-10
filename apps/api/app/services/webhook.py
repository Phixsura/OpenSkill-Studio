"""Webhook service — manage subscriptions and fire async HTTP POSTs."""

import asyncio
import hashlib
import hmac
import ipaddress
import json
import re
import secrets
import socket
from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.webhook import WebhookSubscription

log = structlog.get_logger()

# Known event types for validation
VALID_EVENT_TYPES = frozenset(
    {
        "pack.published",
        "pack.installed",
        "pack.forked",
        "pack.updated",
        "pack.uninstalled",
        # Talent layer (Issue #32)
        "credential.issued",
        "credential.revoked",
        "application.submitted",
        "application.stage_changed",
        "offer.created",
        "placement.started",
        "placement.completed",
        "capability.verified",
        "employer_verification.submitted",
        "outreach.sent",
        "outreach.responded",
        "talent_pool.member_added",
        # Ecosystem intelligence (Issue #35, ADR-016 §13)
        "ecosystem.change",
        # Experimentation (Issue #42, ADR-017 §4.18) — org-scoped only:
        # platform-wide experiments never fan out to tenant webhooks
        "experiment.status_changed",
        "experiment.guardrail_breach",
        "experiment.decision_recorded",
    }
)

# Blocked IP ranges for SSRF protection
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / cloud metadata
    ipaddress.ip_network("0.0.0.0/8"),
    # R171: CGNAT shared address space (RFC 6598) — used by cloud-internal
    # load balancers and Tailscale/WireGuard overlays. Python's is_private is
    # False for it (neither private nor global), so without an explicit entry
    # a webhook to 100.64.x.x reached overlay/means-internal services.
    ipaddress.ip_network("100.64.0.0/10"),
    # R171: NAT64 well-known prefix — 64:ff9b::<v4> routes to the embedded
    # IPv4 through a NAT64 gateway, bypassing every IPv4 check above.
    ipaddress.ip_network("64:ff9b::/96"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 private
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]

MAX_WEBHOOKS_PER_ORG = 25
MAX_EVENTS_PER_WEBHOOK = 20

# Canonical mesh subscription patterns: exact versioned type
# (com.openskill.project.approved.v1) or a prefix wildcard
# (com.openskill.project.*). Segments are lowercase tokens.
_MESH_PATTERN_RE = re.compile(r"com\.openskill\.[a-z0-9_]+(\.[a-z0-9_]+)*(\.v[0-9]+|\.\*)")

# Legacy event name -> canonical mesh catalog name where they differ
# (ADR-018 §12.1). The eco change event only fires for verified changes, so
# it maps onto the catalog's ecosystem.change_verified.
_MESH_NAME_MAP = {
    "ecosystem.change": "ecosystem.change_verified",
}

# Track background delivery tasks so they aren't garbage-collected
# and can be drained on shutdown.
_pending_tasks: set[asyncio.Task] = set()  # type: ignore[type-arg]


async def drain_webhook_tasks(timeout: float = 10.0) -> None:
    """Await all in-flight webhook deliveries. Call from lifespan shutdown."""
    if not _pending_tasks:
        return
    try:
        await asyncio.wait_for(
            asyncio.gather(*_pending_tasks, return_exceptions=True),
            timeout=timeout,
        )
    except TimeoutError:
        log.warning("webhook_drain_timeout", pending=len(_pending_tasks))


# Defect #91: transient receiver failures (429/5xx/network) are retried on
# this backoff schedule — len() extra attempts after the first. 4xx is the
# receiver rejecting THIS event (deterministic); it is never retried.
WEBHOOK_RETRY_SCHEDULE: tuple[float, ...] = (1.0, 5.0, 25.0)


def _is_blocked_url(url: str) -> bool:
    """Check if a URL resolves to a blocked (internal) IP address."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    hostname = parsed.hostname
    if not hostname:
        return True

    # Block obvious internal hostnames
    if hostname in ("localhost", "metadata.google.internal"):
        return True

    try:
        # Resolve DNS and check all resulting IPs
        infos = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for _family, _, _, _, sockaddr in infos:
            if _ip_blocked(ipaddress.ip_address(sockaddr[0])):
                return True
    except (socket.gaierror, ValueError):
        # If DNS resolution fails, block the URL
        return True

    return False


def _ip_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Per-IP SSRF verdict. R251: extracted from _is_blocked_url so the
    IPv4-mapped unwrap is directly testable — macOS getaddrinfo normalizes
    mapped literals to plain v4 before this code runs, but Linux resolvers
    and DNS64 environments hand us ::ffff:<v4> verbatim."""
    # Extract IPv4 from IPv4-mapped IPv6 (e.g. ::ffff:169.254.169.254)
    if ip.version == 6 and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    # Defense-in-depth: catch any unspecified (::, 0.0.0.0), loopback,
    # link-local, or private address regardless of CIDR list gaps
    if ip.is_unspecified or ip.is_loopback or ip.is_link_local or ip.is_private:
        return True
    return any(ip in network for network in _BLOCKED_NETWORKS)


async def _is_blocked_url_async(url: str) -> bool:
    """R171: run the blocking getaddrinfo off the event loop.

    _is_blocked_url resolves DNS with socket.getaddrinfo — a SYNCHRONOUS
    syscall. Called directly from async code it stalls the ENTIRE event loop
    for the resolver timeout; an attacker registering a hostname whose
    authoritative NS answers slowly (or not at all) froze every in-flight
    request on the worker for up to ~30s per lookup, on both the create path
    and every delivery.
    """
    return await asyncio.to_thread(_is_blocked_url, url)


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def _record_webhook_audit(
        self, sub: WebhookSubscription, *, action: str, actor_user_id: str | None
    ) -> None:
        """Defect #105: credential-lifecycle ops (create/delete/rotate) write
        the append-only commercial audit trail. The payload carries url and
        events only — NEVER the secret. Best-effort: an audit hiccup is
        logged, not allowed to fail the operation."""
        if actor_user_id is None:
            return
        try:
            from app.controlplane import facade as cp_facade
            from app.controlplane.services.audit import Actor, record_audit

            tenant = await cp_facade.get_tenant_for_org(self.db, sub.org_id)
            await record_audit(
                self.db,
                actor=Actor(user_id=actor_user_id, type="tenant"),
                action=action,
                target_type="webhook",
                target_id=sub.id,
                tenant_id=tenant.id,
                after={"url": sub.url, "events": list(sub.events or [])},
            )
        except Exception:  # noqa: BLE001 — audit must not break the op
            log.warning(
                "webhook_audit_write_failed", webhook_id=sub.id, audit_action=action
            )

    async def create(
        self,
        org_id: str,
        url: str,
        events: list[str],
        *,
        actor_user_id: str | None = None,
    ) -> WebhookSubscription:
        # SSRF: validate URL doesn't point to internal services
        # (R171: async wrapper — DNS resolution must not block the event loop)
        if await _is_blocked_url_async(url):
            raise AppError(
                "WEBHOOK_URL_BLOCKED",
                "Webhook URL must not point to internal or private addresses",
                422,
            )

        # Validate event types: legacy names from the fixed set, OR canonical
        # mesh patterns (ADR-018 §12 — exact type or 'prefix.*' wildcard).
        # Without this arm, nobody could subscribe to com.openskill.* events
        # through the API at all (marathon R7 defect #7).
        for event in events:
            if event in VALID_EVENT_TYPES:
                continue
            if _MESH_PATTERN_RE.fullmatch(event):
                continue
            raise AppError(
                "INVALID_EVENT",
                f"Unknown event type: {event}. Valid: a com.openskill.* mesh "
                f"pattern or one of: {', '.join(sorted(VALID_EVENT_TYPES))}",
                422,
            )

        # Limit webhooks per org. Defect #102 (#100/#101 family): the bare
        # COUNT was a TOCTOU — lock the Org row first so same-org creators
        # serialize and the cap is exact.
        from app.models.organization import Organization as _Org

        await self.db.execute(
            select(_Org.id).where(_Org.id == org_id).with_for_update()
        )
        count_r = await self.db.execute(
            select(func.count()).where(WebhookSubscription.org_id == org_id)
        )
        existing_count = count_r.scalar_one()
        if existing_count >= MAX_WEBHOOKS_PER_ORG:
            raise AppError(
                "WEBHOOK_LIMIT_REACHED",
                f"Maximum {MAX_WEBHOOKS_PER_ORG} webhooks per organization",
                422,
            )

        secret = secrets.token_hex(32)
        sub = WebhookSubscription(
            org_id=org_id,
            url=url,
            events=events,
            secret=secret,
            active=True,
        )
        self.db.add(sub)
        await self.db.flush()
        log.info("webhook_created", webhook_id=sub.id, org_id=org_id, events=events)
        await self._record_webhook_audit(
            sub, action="webhook.created", actor_user_id=actor_user_id
        )
        return sub

    async def list_subscriptions(self, org_id: str) -> list[WebhookSubscription]:
        result = await self.db.execute(
            select(WebhookSubscription)
            .where(WebhookSubscription.org_id == org_id)
            .order_by(WebhookSubscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def rotate_secret(
        self,
        webhook_id: str,
        org_id: str,
        *,
        actor_user_id: str | None = None,
        immediate: bool = False,
    ) -> WebhookSubscription:
        """Defect #103 (industry staple): retire a signing secret in place —
        same id/url/events, fresh token_hex(32). Org-scoped uniform 404; the
        new secret is returned ONCE, never listed afterwards.

        ADR-018 §12.2 (marathon R14): by default the PREVIOUS secret co-signs
        mesh deliveries for 7 days so receivers can roll keys without a hard
        break. ``immediate=True`` is the leaked-secret path — the old key
        stops signing right now."""
        sub = await self.db.get(WebhookSubscription, webhook_id)
        if sub is None or sub.org_id != org_id:
            raise AppError("WEBHOOK_NOT_FOUND", "Webhook subscription not found", 404)
        from datetime import UTC as _UTC
        from datetime import datetime as _dt

        sub.secret_prev = None if immediate else sub.secret
        sub.secret_rotated_at = _dt.now(_UTC)
        sub.secret = secrets.token_hex(32)
        await self.db.flush()
        await self._record_webhook_audit(
            sub, action="webhook.secret_rotated", actor_user_id=actor_user_id
        )
        return sub

    async def delete(
        self, webhook_id: str, org_id: str, *, actor_user_id: str | None = None
    ) -> None:
        sub = await self.db.get(WebhookSubscription, webhook_id)
        if sub is None or sub.org_id != org_id:
            raise AppError("WEBHOOK_NOT_FOUND", "Webhook subscription not found", 404)
        await self._record_webhook_audit(
            sub, action="webhook.deleted", actor_user_id=actor_user_id
        )
        await self.db.delete(sub)
        await self.db.flush()

    async def trigger_event(
        self,
        org_id: str,
        event_type: str,
        payload: dict,
        *,
        defer_until_commit: bool = False,
    ) -> None:
        """Fire-and-forget HTTP POSTs to all matching active subscriptions.

        This method is fully fail-safe: any DB or delivery error is logged
        and swallowed so it never corrupts the caller's session or transaction.

        defer_until_commit (round 290, defect #80): with the default False the
        HTTP tasks spawn immediately — BEFORE the caller's endpoint commits —
        so a commit failure or rollback leaks a webhook for a write that never
        happened (a phantom event). Pass True to compute the deliveries now
        (the DB reads) but spawn them only on the session's after_commit; a
        rollback simply never fires them.
        """
        # ADR-018 §12 (P2b): mirror every legacy event into the canonical
        # integration event mesh (persistent, signed, retried delivery). The
        # legacy fire-and-forget path below stays for existing subscribers;
        # the mesh row+outbox message joins the caller's transaction so a
        # rollback discards both. Fail-safe: mesh problems never break the
        # business write (same posture as the legacy path).
        try:
            from app.integrations.facade import emit_event as _mesh_emit

            async with self.db.begin_nested():
                await _mesh_emit(
                    self.db,
                    org_id,
                    _MESH_NAME_MAP.get(event_type, event_type),
                    data=payload,
                )
        except Exception:
            log.warning("mesh_event_mirror_failed", org_id=org_id, event_type=event_type)

        try:
            # Use a nested savepoint so any DB error (e.g. missing column
            # before migration runs) doesn't invalidate the caller's session.
            async with self.db.begin_nested():
                # R77[2]: the 'webhooks' entitlement was enforced only at
                # subscription CREATE — suspended/cancelled tenants (whose
                # SUSPENSION_MASKED_KEYS turn webhooks off) and plan
                # downgrades kept DELIVERING through pre-existing
                # subscriptions forever. Gate the delivery path itself.
                from app.controlplane import facade as cp_facade
                from app.controlplane.services.entitlements import get_effective

                tenant = await cp_facade.get_tenant_for_org(self.db, org_id)
                eff = await get_effective(self.db, tenant)
                if not eff.values.get("webhooks"):
                    log.info(
                        "webhook_delivery_blocked_entitlement",
                        org_id=org_id,
                        webhook_event=event_type,
                    )
                    return
                result = await self.db.execute(
                    select(WebhookSubscription).where(
                        WebhookSubscription.org_id == org_id,
                        WebhookSubscription.active.is_(True),
                    )
                )
                subs = list(result.scalars().all())
        except Exception:
            log.warning("webhook_query_failed", org_id=org_id, webhook_event=event_type)
            return

        # Collect delivery data before creating background tasks
        deliveries = []
        for sub in subs:
            if sub.events and event_type not in sub.events:
                continue
            deliveries.append(
                {
                    "url": sub.url,
                    "secret": sub.secret,
                    "webhook_id": sub.id,
                }
            )

        if not deliveries:
            return

        def _spawn_all() -> None:
            # Fire-and-forget: don't block the caller.
            # Keep strong references so tasks aren't GC'd before completion.
            for delivery in deliveries:
                task = asyncio.create_task(
                    self._deliver_background(
                        delivery["url"],
                        delivery["secret"],
                        delivery["webhook_id"],
                        event_type,
                        payload,
                    )
                )
                _pending_tasks.add(task)
                task.add_done_callback(_pending_tasks.discard)

        if not defer_until_commit:
            _spawn_all()
            return

        from sqlalchemy import event as sa_event

        # Rounds 293/296: emits inside a begin_nested savepoint are a
        # SUPPORTED, routine path — the outbox runner wraps every handler in
        # one, so the guardrail sweep's breach emit lands here. The observed
        # contract (pinned by five DB kill-proofs in test_exp_webhooks_db —
        # the alarm if a SQLAlchemy upgrade shifts event semantics):
        # savepoint releases -> delivers at the outer commit; the emit's own
        # savepoint rolls back -> cancelled; an UNRELATED later savepoint
        # rollback -> still delivers; a real rollback -> cancelled, and never
        # rides a later commit (#81).
        if self.db.sync_session.in_nested_transaction():
            log.debug(
                "webhook_defer_inside_savepoint",
                org_id=org_id,
                webhook_event=event_type,
            )

        # #81 (round 291): a once-listener SURVIVES a rollback — if the same
        # session later commits unrelated work (the retry pattern), the
        # rolled-back transaction's event would fire anyway. The rollback
        # listener cancels the pending spawn.
        cancelled = False

        @sa_event.listens_for(self.db.sync_session, "after_commit", once=True)
        def _fire_on_commit(_session) -> None:  # pragma: no branch
            # Runs in the loop's thread (greenlet context) — create_task is
            # safe here. A rollback means this listener never fires, which is
            # exactly the phantom-prevention contract.
            if not cancelled:
                _spawn_all()

        @sa_event.listens_for(self.db.sync_session, "after_rollback", once=True)
        def _cancel_on_rollback(_session) -> None:  # pragma: no branch
            nonlocal cancelled
            cancelled = True

    @staticmethod
    async def _deliver_background(
        url: str,
        secret: str,
        webhook_id: str,
        event_type: str,
        payload: dict,
    ) -> None:
        """Send a single webhook delivery. Best-effort, errors are logged not raised.

        Re-validates the URL at delivery time via _is_blocked_url to catch
        DNS rebinding. The TOCTOU window is microseconds within this function.
        We use the original URL for httpx so TLS cert verification works
        correctly (certs are issued for hostnames, not IPs).
        """
        import httpx

        # Re-validate URL at delivery time to catch DNS rebinding
        # (R171: async wrapper — DNS resolution must not block the event loop)
        if await _is_blocked_url_async(url):
            log.warning(
                "webhook_delivery_blocked_dns_rebind",
                webhook_id=webhook_id,
                url=url,
            )
            return

        # Validate scheme — only HTTPS in production (HTTP allowed for dev)
        from urllib.parse import urlparse

        parsed = urlparse(url)
        if parsed.scheme not in ("https", "http"):
            log.warning("webhook_invalid_scheme", webhook_id=webhook_id, url=url)
            return

        body = json.dumps(
            {
                "event": event_type,
                "payload": payload,
                "timestamp": datetime.now(UTC).isoformat(),
                "webhook_id": webhook_id,
            },
            default=str,
        )
        signature = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()

        # Defect #91: retry transient failures (429/5xx/network error) on the
        # backoff schedule; 2xx/3xx stops, 4xx (minus 429) never retries.
        attempts = 1 + len(WEBHOOK_RETRY_SCHEDULE)
        for attempt in range(1, attempts + 1):
            if attempt > 1:
                await asyncio.sleep(WEBHOOK_RETRY_SCHEDULE[attempt - 2])
                # The backoff window is long enough for a DNS rebind —
                # re-validate the target before every retry, not just once
                if await _is_blocked_url_async(url):
                    log.warning(
                        "webhook_delivery_blocked_dns_rebind",
                        webhook_id=webhook_id,
                        url=url,
                    )
                    return
            status: int | None = None
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # R171: stream and discard the response — a plain .post()
                    # buffers the receiver's ENTIRE body into memory. The
                    # receiver is an org-controlled server: one returning
                    # multi-GB bodies across 25 subscriptions per org was an
                    # unbounded memory amplification against the API worker.
                    # We only care that the POST was accepted; never read the
                    # body.
                    async with client.stream(
                        "POST",
                        url,
                        content=body,
                        headers={
                            "Content-Type": "application/json",
                            "X-Webhook-Signature": signature,
                            "X-Webhook-Event": event_type,
                        },
                    ) as resp:
                        status = resp.status_code
            except Exception:
                log.warning(
                    "webhook_delivery_failed",
                    webhook_id=webhook_id,
                    webhook_event=event_type,
                    url=url,
                    attempt=attempt,
                )
            if status is not None and status < 500 and status != 429:
                # 2xx/3xx accepted; a non-429 4xx is a deterministic
                # rejection of THIS event — retrying it is abuse
                log.info(
                    "webhook_delivered",
                    webhook_id=webhook_id,
                    webhook_event=event_type,
                    status=status,
                    attempt=attempt,
                )
                return
            if status is not None:
                log.warning(
                    "webhook_delivery_retryable",
                    webhook_id=webhook_id,
                    webhook_event=event_type,
                    status=status,
                    attempt=attempt,
                )
        log.warning(
            "webhook_delivery_exhausted",
            webhook_id=webhook_id,
            webhook_event=event_type,
            url=url,
            attempts=attempts,
        )
