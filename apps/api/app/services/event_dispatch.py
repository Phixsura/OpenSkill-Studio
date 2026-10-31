"""Event dispatch engine — routes platform events to subscribed app installations.

Events flow: platform action → emit_event() → match subscriptions → deliver
via webhook HTTP POST or sandbox function invocation.
"""

import asyncio
import hashlib
import hmac
import json
from datetime import UTC, datetime

import httpx
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppAutomationRule,
    AppEventSubscription,
    AppInstallation,
    DeveloperApp,
    InstallationStatus,
)

log = structlog.get_logger()


# ── SSRF protection ─────────────────────────────────────


def _is_safe_url(url: str) -> bool:
    """Reject URLs targeting private/loopback/metadata addresses."""
    import ipaddress
    import socket
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False

        # Block known metadata endpoints
        blocked = {
            "localhost", "metadata.google.internal",
            "169.254.169.254",
        }
        if hostname.lower() in blocked:
            return False

        # Resolve and check all addresses
        addrs = socket.getaddrinfo(hostname, parsed.port or 443, proto=socket.IPPROTO_TCP)
        for _, _, _, _, sockaddr in addrs:
            ip = ipaddress.ip_address(sockaddr[0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
    except (ValueError, socket.gaierror, OSError):
        return False
    return True


# ── Canonical Event Types ────────────────────────────────

CANONICAL_EVENTS = frozenset({
    # Organization lifecycle
    "org.created", "org.updated", "org.member_added", "org.member_removed",
    # Cohort lifecycle
    "cohort.created", "cohort.updated", "cohort.member_added", "cohort.member_removed",
    # Project / Submission
    "project.created", "project.published", "project.archived",
    "submission.created", "submission.completed", "submission.graded",
    # Packs
    "pack.published", "pack.installed", "pack.updated", "pack.uninstalled", "pack.forked",
    # Workflows
    "workflow.run_started", "workflow.run_completed", "workflow.run_failed",
    "workflow.step_completed", "workflow.review_submitted",
    # Talent
    "talent.capability_verified", "talent.credential_issued", "talent.credential_revoked",
    "talent.application_submitted", "talent.application_stage_changed",
    "talent.offer_created", "talent.placement_started",
    # Marketplace
    "marketplace.listing_published", "marketplace.purchase_completed",
    "marketplace.license_granted", "marketplace.license_revoked",
    # Evaluation
    "evaluation.completed", "evaluation.failed",
    # App lifecycle
    "app.installed", "app.uninstalled", "app.updated",
})

# Max delivery attempts for webhook retry
MAX_DELIVERY_ATTEMPTS = 3
RETRY_DELAYS = [10, 60, 300]  # seconds


# ── Event model ──────────────────────────────────────────


class PlatformEvent:
    """A platform event to be dispatched to subscribers."""

    def __init__(
        self,
        event_type: str,
        data: dict,
        *,
        org_id: str | None = None,
        user_id: str | None = None,
        timestamp: str | None = None,
    ):
        self.event_type = event_type
        self.data = data
        self.org_id = org_id
        self.user_id = user_id
        self.timestamp = timestamp or datetime.now(UTC).isoformat()
        self.event_id = hashlib.sha256(
            f"{event_type}:{self.timestamp}:{json.dumps(data, sort_keys=True)}".encode()
        ).hexdigest()[:26]

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "data": self.data,
            "org_id": self.org_id,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
        }


# ── Dispatch engine ──────────────────────────────────────


class EventDispatcher:
    """Dispatches platform events to subscribed app installations."""

    def __init__(self):
        self._http_client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0),
                follow_redirects=False,
                trust_env=False,
            )
        return self._http_client

    async def emit(self, db: AsyncSession, event: PlatformEvent) -> int:
        """Emit an event — find all matching subscriptions and deliver.

        Returns the number of deliveries attempted.
        """
        log.info(
            "event_emitted",
            event_type=event.event_type,
            event_id=event.event_id,
            org_id=event.org_id,
        )

        # Find matching subscriptions
        q = (
            select(AppEventSubscription, AppInstallation, DeveloperApp)
            .join(
                AppInstallation,
                AppEventSubscription.installation_id == AppInstallation.id,
            )
            .join(DeveloperApp, AppInstallation.app_id == DeveloperApp.id)
            .where(
                AppEventSubscription.event_type == event.event_type,
                AppEventSubscription.enabled.is_(True),
                AppInstallation.status == InstallationStatus.ACTIVE,
            )
        )

        # Fail closed: always scope to org. If no org_id, skip dispatch.
        if not event.org_id:
            log.debug("event_skip_no_org", event_type=event.event_type)
            return 0
        q = q.where(AppInstallation.org_id == event.org_id)

        result = await db.execute(q)
        rows = result.all()

        if not rows:
            return 0

        delivery_count = 0
        for sub, installation, app in rows:
            # Apply filter expression if defined
            if sub.filter_expression and not self._matches_filter(
                event.data, sub.filter_expression
            ):
                continue

            # Deliver via webhook
            if app.webhook_url:
                asyncio.create_task(
                    self._deliver_webhook(
                        app=app,
                        installation=installation,
                        event=event,
                    )
                )
                delivery_count += 1

        # Check automation rules
        rule_count = await self._process_automation_rules(db, event)
        delivery_count += rule_count

        log.info(
            "event_dispatched",
            event_type=event.event_type,
            deliveries=delivery_count,
        )
        return delivery_count

    def _matches_filter(self, data: dict, filter_expr: dict) -> bool:
        """Evaluate a simple filter expression against event data.

        Filter format: {"field": "path.to.field", "operator": "eq|gte|lte|contains", "value": X}
        """
        try:
            field_path = filter_expr.get("field", "")
            operator = filter_expr.get("operator", "eq")
            expected = filter_expr.get("value")

            # Navigate nested path
            value = data
            for part in field_path.split("."):
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return False

            if operator == "eq":
                return value == expected
            if operator == "neq":
                return value != expected
            if operator == "gte":
                return value is not None and value >= expected
            if operator == "lte":
                return value is not None and value <= expected
            if operator == "contains":
                return expected in (value or "")
            if operator == "in":
                return value in (expected or [])
            return True
        except Exception:
            return True  # Default: pass filter on error

    async def _deliver_webhook(
        self,
        app: DeveloperApp,
        installation: AppInstallation,
        event: PlatformEvent,
    ) -> None:
        """Deliver event via HMAC-signed webhook HTTP POST with retry.

        SSRF protection: require https, reject private/loopback addresses.
        """
        # SSRF: require https
        if not app.webhook_url or not app.webhook_url.startswith("https://"):
            log.warning("webhook_rejected_not_https", app_id=app.id)
            return

        # SSRF: reject private/loopback hosts
        if not _is_safe_url(app.webhook_url):
            log.warning("webhook_rejected_ssrf", app_id=app.id, url=app.webhook_url)
            return
        payload = json.dumps({
            "event": event.to_dict(),
            "installation_id": installation.id,
            "app_id": app.id,
        }).encode()

        # HMAC-SHA256 signature using app's webhook secret
        signature = ""
        if app.webhook_secret_hash:
            signature = hmac.new(
                app.webhook_secret_hash.encode(),
                payload,
                hashlib.sha256,
            ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "X-OpenSkill-Event": event.event_type,
            "X-OpenSkill-Delivery": event.event_id,
            "X-OpenSkill-Signature": f"sha256={signature}",
            "User-Agent": "OpenSkill-Webhook/1.0",
        }

        client = await self._get_client()

        for attempt in range(MAX_DELIVERY_ATTEMPTS):
            try:
                resp = await client.post(
                    app.webhook_url,
                    content=payload,
                    headers=headers,
                )
                if resp.status_code < 400:
                    log.info(
                        "webhook_delivered",
                        app_id=app.id,
                        event=event.event_type,
                        status=resp.status_code,
                        attempt=attempt + 1,
                    )
                    return
                log.warning(
                    "webhook_delivery_failed",
                    app_id=app.id,
                    status=resp.status_code,
                    attempt=attempt + 1,
                )
            except Exception as exc:
                log.warning(
                    "webhook_delivery_error",
                    app_id=app.id,
                    error=str(exc),
                    attempt=attempt + 1,
                )

            # Retry with delay
            if attempt < MAX_DELIVERY_ATTEMPTS - 1:
                await asyncio.sleep(RETRY_DELAYS[attempt])

        log.error(
            "webhook_delivery_exhausted",
            app_id=app.id,
            event=event.event_type,
        )

    async def _process_automation_rules(
        self, db: AsyncSession, event: PlatformEvent
    ) -> int:
        """Process automation rules triggered by this event."""
        q = (
            select(AppAutomationRule, AppInstallation)
            .join(
                AppInstallation,
                AppAutomationRule.installation_id == AppInstallation.id,
            )
            .where(
                AppAutomationRule.trigger_event == event.event_type,
                AppAutomationRule.enabled.is_(True),
                AppInstallation.status == InstallationStatus.ACTIVE,
            )
        )

        # Fail closed: always scope to org
        if not event.org_id:
            return 0
        q = q.where(AppInstallation.org_id == event.org_id)

        result = await db.execute(q)
        rows = result.all()
        executed = 0

        for rule, _installation in rows:
            # Check rate limit
            if rule.execution_count >= rule.max_executions_per_hour:
                log.warning(
                    "automation_rule_rate_limited",
                    rule_id=rule.id,
                    count=rule.execution_count,
                )
                continue

            # Apply trigger filter
            if rule.trigger_filter and not self._matches_filter(
                event.data, rule.trigger_filter
            ):
                continue

            # Execute action
            try:
                await self._execute_rule_action(rule, event)
                rule.execution_count += 1
                rule.last_executed_at = datetime.now(UTC)
                await db.flush()
                executed += 1
                log.info(
                    "automation_rule_executed",
                    rule_id=rule.id,
                    action=rule.action_type.value
                    if hasattr(rule.action_type, "value")
                    else rule.action_type,
                )
            except Exception as exc:
                log.error(
                    "automation_rule_failed",
                    rule_id=rule.id,
                    error=str(exc),
                )

        return executed

    async def _execute_rule_action(
        self, rule: AppAutomationRule, event: PlatformEvent
    ) -> None:
        """Execute an automation rule's action."""
        action_type = (
            rule.action_type.value
            if hasattr(rule.action_type, "value")
            else rule.action_type
        )
        config = rule.action_config

        if action_type == "webhook":
            url = config.get("url")
            if not url or not url.startswith("https://"):
                return
            if not _is_safe_url(url):
                log.warning("rule_webhook_rejected_ssrf", rule_id=rule.id, url=url)
                return
            method = config.get("method", "POST").upper()

            # Template substitution in body
            body = config.get("body_template", {})
            body_str = json.dumps(body)
            # Replace {{event.data.xxx}} placeholders
            event_dict = event.to_dict()
            for key, val in self._flatten_dict(event_dict).items():
                body_str = body_str.replace(f"{{{{{key}}}}}", str(val))

            client = await self._get_client()
            headers = config.get("headers", {})
            headers["Content-Type"] = "application/json"

            if method == "POST":
                await client.post(url, content=body_str.encode(), headers=headers)
            elif method == "PUT":
                await client.put(url, content=body_str.encode(), headers=headers)

        elif action_type == "notification":
            # In-app notification — would create a Notification model entry
            log.info(
                "automation_notification",
                message=config.get("message", ""),
                event=event.event_type,
            )

    def _flatten_dict(self, d: dict, prefix: str = "") -> dict[str, str]:
        """Flatten nested dict for template substitution."""
        items: dict[str, str] = {}
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, key))
            else:
                items[key] = str(v) if v is not None else ""
        return items

    async def close(self) -> None:
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()


# ── Singleton ────────────────────────────────────────────

event_dispatcher = EventDispatcher()


# ── Convenience ──────────────────────────────────────────


async def emit_event(
    db: AsyncSession,
    event_type: str,
    data: dict,
    *,
    org_id: str | None = None,
    user_id: str | None = None,
) -> int:
    """Convenience function to emit a platform event."""
    event = PlatformEvent(
        event_type=event_type,
        data=data,
        org_id=org_id,
        user_id=user_id,
    )
    return await event_dispatcher.emit(db, event)
