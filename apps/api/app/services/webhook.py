"""Webhook service — manage subscriptions and fire async HTTP POSTs."""

import asyncio
import hashlib
import hmac
import ipaddress
import json
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
VALID_EVENT_TYPES = frozenset({
    "pack.published",
    "pack.installed",
    "pack.forked",
    "pack.updated",
    "pack.uninstalled",
})

# Blocked IP ranges for SSRF protection
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # link-local / cloud metadata
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),  # IPv6 private
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
]

MAX_WEBHOOKS_PER_ORG = 25
MAX_EVENTS_PER_WEBHOOK = 20


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
            ip = ipaddress.ip_address(sockaddr[0])
            # Extract IPv4 from IPv4-mapped IPv6 (e.g. ::ffff:169.254.169.254)
            # to prevent bypass via IPv4-mapped IPv6 addresses
            if ip.version == 6 and ip.ipv4_mapped:
                ip = ip.ipv4_mapped
            for network in _BLOCKED_NETWORKS:
                if ip in network:
                    return True
    except (socket.gaierror, ValueError):
        # If DNS resolution fails, block the URL
        return True

    return False


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        org_id: str,
        url: str,
        events: list[str],
    ) -> WebhookSubscription:
        # SSRF: validate URL doesn't point to internal services
        if _is_blocked_url(url):
            raise AppError(
                "WEBHOOK_URL_BLOCKED",
                "Webhook URL must not point to internal or private addresses",
                422,
            )

        # Validate event types
        for event in events:
            if event not in VALID_EVENT_TYPES:
                raise AppError(
                    "INVALID_EVENT",
                    f"Unknown event type: {event}. Valid: {', '.join(sorted(VALID_EVENT_TYPES))}",
                    422,
                )

        # Limit webhooks per org (use SELECT COUNT for efficiency)
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
        return sub

    async def list_subscriptions(self, org_id: str) -> list[WebhookSubscription]:
        result = await self.db.execute(
            select(WebhookSubscription)
            .where(WebhookSubscription.org_id == org_id)
            .order_by(WebhookSubscription.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, webhook_id: str, org_id: str) -> None:
        sub = await self.db.get(WebhookSubscription, webhook_id)
        if sub is None or sub.org_id != org_id:
            raise AppError("WEBHOOK_NOT_FOUND", "Webhook subscription not found", 404)
        await self.db.delete(sub)
        await self.db.flush()

    async def trigger_event(self, org_id: str, event_type: str, payload: dict) -> None:
        """Fire-and-forget HTTP POSTs to all matching active subscriptions.

        This method is fully fail-safe: any DB or delivery error is logged
        and swallowed so it never corrupts the caller's session or transaction.
        """
        try:
            # Use a nested savepoint so any DB error (e.g. missing column
            # before migration runs) doesn't invalidate the caller's session.
            async with self.db.begin_nested():
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
            deliveries.append({
                "url": sub.url,
                "secret": sub.secret,
                "webhook_id": sub.id,
            })

        if not deliveries:
            return

        # Fire-and-forget: don't block the caller
        for delivery in deliveries:
            asyncio.create_task(
                self._deliver_background(
                    delivery["url"],
                    delivery["secret"],
                    delivery["webhook_id"],
                    event_type,
                    payload,
                )
            )

    @staticmethod
    async def _deliver_background(
        url: str,
        secret: str,
        webhook_id: str,
        event_type: str,
        payload: dict,
    ) -> None:
        """Send a single webhook delivery. Best-effort, errors are logged not raised."""
        import httpx

        # Re-validate URL at delivery time to prevent DNS rebinding attacks.
        # An attacker could register a webhook with a public IP, then rebind
        # the domain to an internal IP before delivery fires.
        if _is_blocked_url(url):
            log.warning(
                "webhook_delivery_blocked_dns_rebind",
                webhook_id=webhook_id,
                url=url,
            )
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
        signature = hmac.new(
            secret.encode(), body.encode(), hashlib.sha256
        ).hexdigest()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    url,
                    content=body,
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event_type,
                    },
                )
        except Exception:
            log.warning(
                "webhook_delivery_failed",
                webhook_id=webhook_id,
                webhook_event=event_type,
                url=url,
            )
