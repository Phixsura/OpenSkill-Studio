"""App notification service — notify stakeholders about app lifecycle events.

Sends in-app notifications to:
- Org admins when apps are installed/uninstalled
- Developers when their apps are reviewed/installed/uninstalled
- Platform admins for review queue updates
"""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification

log = structlog.get_logger()


async def notify_app_installed(
    db: AsyncSession,
    *,
    app_name: str,
    app_id: str,
    org_id: str,
    installed_by: str,
    developer_user_id: str,
) -> None:
    """Notify developer that their app was installed."""
    notification = Notification(
        user_id=developer_user_id,
        title="App Installed",
        message=f'Your app "{app_name}" was installed in a new organization.',
        type="app_installed",
        link=f"/dashboard/developer/apps/{app_id}/stats",
    )
    db.add(notification)
    log.info("notification_app_installed", app_id=app_id, org_id=org_id)


async def notify_app_uninstalled(
    db: AsyncSession,
    *,
    app_name: str,
    app_id: str,
    org_id: str,
    developer_user_id: str,
) -> None:
    """Notify developer that their app was uninstalled."""
    notification = Notification(
        user_id=developer_user_id,
        title="App Uninstalled",
        message=f'Your app "{app_name}" was uninstalled from an organization.',
        type="app_uninstalled",
        link=f"/dashboard/developer/apps/{app_id}/stats",
    )
    db.add(notification)
    log.info("notification_app_uninstalled", app_id=app_id, org_id=org_id)


async def notify_review_submitted(
    db: AsyncSession,
    *,
    app_name: str,
    app_id: str,
    developer_user_id: str,
) -> None:
    """Notify developer that their review was submitted."""
    notification = Notification(
        user_id=developer_user_id,
        title="App Submitted for Review",
        message=f'Your app "{app_name}" has been submitted for platform review.',
        type="app_review_submitted",
        link=f"/dashboard/developer/apps/{app_id}",
    )
    db.add(notification)
    log.info("notification_review_submitted", app_id=app_id)


async def notify_review_decided(
    db: AsyncSession,
    *,
    app_name: str,
    app_id: str,
    developer_user_id: str,
    decision: str,
    notes: str | None = None,
) -> None:
    """Notify developer of review decision."""
    status_text = "approved ✅" if decision == "approved" else "rejected ❌"
    message = f'Your app "{app_name}" has been {status_text}.'
    if notes:
        message += f" Notes: {notes}"

    notification = Notification(
        user_id=developer_user_id,
        title=f"App Review {decision.capitalize()}",
        message=message,
        type=f"app_review_{decision}",
        link=f"/dashboard/developer/apps/{app_id}",
    )
    db.add(notification)
    log.info("notification_review_decided", app_id=app_id, decision=decision)


async def notify_app_revoked(
    db: AsyncSession,
    *,
    app_name: str,
    app_id: str,
    developer_user_id: str,
    reason: str,
) -> None:
    """Notify developer that their app was revoked."""
    notification = Notification(
        user_id=developer_user_id,
        title="App Revoked ⚠️",
        message=f'Your app "{app_name}" has been revoked. Reason: {reason}',
        type="app_revoked",
        link=f"/dashboard/developer/apps/{app_id}",
    )
    db.add(notification)
    log.info("notification_app_revoked", app_id=app_id, reason=reason)


async def notify_version_published(
    db: AsyncSession,
    *,
    app_name: str,
    app_id: str,
    version: str,
    developer_user_id: str,
) -> None:
    """Notify developer that their version was published."""
    notification = Notification(
        user_id=developer_user_id,
        title="Version Published",
        message=f'Version {version} of "{app_name}" is now live.',
        type="app_version_published",
        link=f"/dashboard/developer/apps/{app_id}/versions",
    )
    db.add(notification)
    log.info("notification_version_published", app_id=app_id, version=version)
