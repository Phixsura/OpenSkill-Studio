"""App Changelog Notify — send notifications when new versions are released.

Manages release notification delivery:
- Define notification templates
- Batch notify subscribers on release
- Track delivery status
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class NotificationTemplate:
    """A notification template for releases."""

    template_id: str
    channel: str  # "email", "slack", "webhook"
    subject_template: str
    body_template: str


@dataclass
class NotificationDelivery:
    """Record of a sent notification."""

    delivery_id: str
    version: str
    channel: str
    recipient: str
    sent_at: float = field(default_factory=time.time)
    success: bool = True


class AppChangelogNotify:
    """Send notifications on new releases."""

    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], NotificationTemplate] = {}
        self._deliveries: dict[str, list[NotificationDelivery]] = {}

    def register_template(
        self,
        installation_id: str,
        template_id: str,
        channel: str,
        subject_template: str,
        body_template: str,
    ) -> NotificationTemplate:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not template_id:
            raise ValueError("template_id is required")

        tpl = NotificationTemplate(
            template_id=template_id, channel=channel,
            subject_template=subject_template, body_template=body_template,
        )
        self._templates[(installation_id, template_id)] = tpl
        return tpl

    def notify_release(
        self,
        installation_id: str,
        version: str,
        recipients: list[str],
        template_id: str,
        now: float | None = None,
    ) -> list[NotificationDelivery]:
        """Send release notifications to recipients."""
        key = (installation_id, template_id)
        tpl = self._templates.get(key)
        if tpl is None:
            raise KeyError(f"Template {template_id} not found")

        now = now or time.time()
        deliveries: list[NotificationDelivery] = []
        for i, recipient in enumerate(recipients):
            d = NotificationDelivery(
                delivery_id=f"d-{version}-{i}",
                version=version, channel=tpl.channel,
                recipient=recipient, sent_at=now,
            )
            deliveries.append(d)

        self._deliveries.setdefault(installation_id, []).extend(deliveries)
        return deliveries

    def get_deliveries(
        self, installation_id: str, version: str | None = None, limit: int = 50
    ) -> list[NotificationDelivery]:
        if not installation_id:
            raise ValueError("installation_id is required")
        ds = self._deliveries.get(installation_id, [])
        if version:
            ds = [d for d in ds if d.version == version]
        return list(reversed(ds[-limit:]))

    def delivery_count(self, installation_id: str) -> int:
        return len(self._deliveries.get(installation_id, []))
