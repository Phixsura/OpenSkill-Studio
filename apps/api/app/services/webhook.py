"""Webhook service — manage subscriptions and fire async HTTP POSTs."""

import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.models.webhook import WebhookSubscription

log = structlog.get_logger()


class WebhookService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        org_id: str,
        url: str,
        events: list[str],
    ) -> WebhookSubscription:
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
        """Fire async HTTP POST to all matching active subscriptions for an org."""
        result = await self.db.execute(
            select(WebhookSubscription).where(
                WebhookSubscription.org_id == org_id,
                WebhookSubscription.active.is_(True),
            )
        )
        subs = list(result.scalars().all())

        for sub in subs:
            # Check if subscription is interested in this event type
            if sub.events and event_type not in sub.events:
                continue
            await self._deliver(sub, event_type, payload)

    @staticmethod
    async def _deliver(sub: WebhookSubscription, event_type: str, payload: dict) -> None:
        """Send a single webhook delivery. Best-effort, errors are logged not raised."""
        import httpx

        body = json.dumps(
            {
                "event": event_type,
                "payload": payload,
                "timestamp": datetime.now(UTC).isoformat(),
                "webhook_id": sub.id,
            },
            default=str,
        )
        signature = hmac.new(
            sub.secret.encode(), body.encode(), hashlib.sha256
        ).hexdigest()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    sub.url,
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
                webhook_id=sub.id,
                event=event_type,
                url=sub.url,
            )
