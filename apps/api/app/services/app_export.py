"""App export service — export app data for backup and migration.

Provides serialization of app configuration, versions, and installation
data for backup, migration between environments, and developer tooling.
"""

from datetime import UTC, datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppAutomationRule,
    AppEventSubscription,
    AppInstallation,
    AppSecret,
    AppUiExtension,
    AppVersion,
    DeveloperApp,
)

log = structlog.get_logger()


async def export_app_config(db: AsyncSession, app_id: str) -> dict:
    """Export full app configuration as a portable JSON structure.

    Includes app metadata, all versions (with manifests), UI extensions,
    and signing keys. Does NOT include installation-specific data or secrets.
    """
    app_result = await db.execute(
        select(DeveloperApp).where(DeveloperApp.id == app_id)
    )
    app = app_result.scalar_one_or_none()
    if not app:
        return {"error": "App not found"}

    # Versions
    versions_result = await db.execute(
        select(AppVersion)
        .where(AppVersion.app_id == app_id)
        .order_by(AppVersion.created_at.desc())
    )
    versions = [
        {
            "version": v.version,
            "manifest": v.manifest,
            "changelog": v.changelog,
            "content_hash": v.content_hash,
            "review_status": v.review_status.value if hasattr(v.review_status, "value") else v.review_status,
            "min_platform_version": v.min_platform_version,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions_result.scalars().all()
    ]

    # UI Extensions
    ui_result = await db.execute(
        select(AppUiExtension).where(AppUiExtension.app_id == app_id)
    )
    ui_extensions = [
        {
            "surface": ext.surface.value if hasattr(ext.surface, "value") else ext.surface,
            "title": ext.title,
            "entry_path": ext.entry_path,
            "viewport_width": ext.viewport_width,
            "viewport_height": ext.viewport_height,
        }
        for ext in ui_result.scalars().all()
    ]

    return {
        "export_version": "1.0",
        "exported_at": datetime.now(UTC).isoformat(),
        "app": {
            "name": app.name,
            "slug": app.slug,
            "description": app.description,
            "category": app.category.value if hasattr(app.category, "value") else app.category,
            "visibility": app.visibility.value if hasattr(app.visibility, "value") else app.visibility,
            "homepage_url": app.homepage_url,
            "privacy_policy_url": app.privacy_policy_url,
            "webhook_url": app.webhook_url,
            "manifest": app.manifest,
        },
        "versions": versions,
        "ui_extensions": ui_extensions,
        "version_count": len(versions),
    }


async def export_installation_config(
    db: AsyncSession, installation_id: str
) -> dict:
    """Export installation configuration (no secrets).

    Useful for migrating an installation to a different environment.
    """
    inst_result = await db.execute(
        select(AppInstallation).where(AppInstallation.id == installation_id)
    )
    inst = inst_result.scalar_one_or_none()
    if not inst:
        return {"error": "Installation not found"}

    # Event subscriptions
    subs_result = await db.execute(
        select(AppEventSubscription)
        .where(AppEventSubscription.installation_id == installation_id)
    )
    subscriptions = [
        {
            "event_type": s.event_type,
            "enabled": s.enabled,
            "filter_expression": s.filter_expression,
        }
        for s in subs_result.scalars().all()
    ]

    # Automation rules
    rules_result = await db.execute(
        select(AppAutomationRule)
        .where(AppAutomationRule.installation_id == installation_id)
    )
    rules = [
        {
            "name": r.name,
            "trigger_event": r.trigger_event,
            "trigger_filter": r.trigger_filter,
            "action_type": r.action_type.value if hasattr(r.action_type, "value") else r.action_type,
            "action_config": r.action_config,
            "enabled": r.enabled,
            "max_executions_per_hour": r.max_executions_per_hour,
        }
        for r in rules_result.scalars().all()
    ]

    # Secret keys (names only, never values)
    secrets_result = await db.execute(
        select(AppSecret.key, AppSecret.description)
        .where(AppSecret.installation_id == installation_id)
    )
    secret_keys = [
        {"key": row.key, "description": row.description}
        for row in secrets_result.all()
    ]

    return {
        "export_version": "1.0",
        "exported_at": datetime.now(UTC).isoformat(),
        "installation": {
            "app_id": inst.app_id,
            "app_version_id": inst.app_version_id,
            "org_id": inst.org_id,
            "granted_permissions": inst.granted_permissions,
            "config": inst.config,
            "pinned_version": inst.pinned_version,
        },
        "event_subscriptions": subscriptions,
        "automation_rules": rules,
        "secret_keys": secret_keys,
    }
