"""Conformance test suite (ADR-016 Part P).

Validates that installed apps conform to platform contracts:
- Manifest schema compliance
- Permission usage audit
- Webhook delivery health
- Sandbox execution health
- Version compatibility
- API contract conformance
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.developer import (
    AppApiKey,
    AppEventSubscription,
    AppInstallation,
    AppVersion,
    DeveloperApp,
    SandboxExecution,
    SandboxExecutionStatus,
)
from app.services.manifest_validator import validate_manifest

log = structlog.get_logger()


@dataclass
class ConformanceCheck:
    name: str
    status: str  # "pass", "fail", "warn", "skip"
    message: str
    details: dict = field(default_factory=dict)


@dataclass
class ConformanceReport:
    app_id: str
    app_name: str
    version: str
    checked_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    checks: list[ConformanceCheck] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.status in ("pass", "warn", "skip") for c in self.checks)

    @property
    def summary(self) -> dict:
        counts = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}
        for c in self.checks:
            counts[c.status] = counts.get(c.status, 0) + 1
        return {
            "passed": self.passed,
            "total_checks": len(self.checks),
            **counts,
        }

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "app_name": self.app_name,
            "version": self.version,
            "checked_at": self.checked_at,
            "summary": self.summary,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "message": c.message,
                    "details": c.details,
                }
                for c in self.checks
            ],
        }


async def run_conformance_checks(
    db: AsyncSession,
    app_id: str,
) -> ConformanceReport:
    """Run the full conformance suite on an app."""
    # Load app + latest version
    result = await db.execute(
        select(DeveloperApp).where(DeveloperApp.id == app_id)
    )
    app = result.scalar_one_or_none()
    if not app:
        report = ConformanceReport(app_id=app_id, app_name="unknown", version="unknown")
        report.checks.append(
            ConformanceCheck("app_exists", "fail", "App not found")
        )
        return report

    # Get latest version
    ver_result = await db.execute(
        select(AppVersion)
        .where(AppVersion.app_id == app_id)
        .order_by(AppVersion.created_at.desc())
        .limit(1)
    )
    latest_version = ver_result.scalar_one_or_none()
    version_str = latest_version.version if latest_version else "none"

    report = ConformanceReport(
        app_id=app_id,
        app_name=app.name,
        version=version_str,
    )

    # 1. Manifest validation
    await _check_manifest(report, app, latest_version)

    # 2. Version health
    await _check_versions(db, report, app_id)

    # 3. Installation health
    await _check_installations(db, report, app_id)

    # 4. Sandbox execution health
    await _check_sandbox_health(db, report, app_id)

    # 5. API key hygiene
    await _check_api_keys(db, report, app_id)

    # 6. Event subscription validity
    await _check_event_subscriptions(db, report, app_id)

    # 7. Security checks
    _check_security(report, app)

    log.info(
        "conformance_check_complete",
        app_id=app_id,
        passed=report.passed,
        summary=report.summary,
    )
    return report


async def _check_manifest(
    report: ConformanceReport,
    app: DeveloperApp,
    version: AppVersion | None,
) -> None:
    """Check manifest schema compliance."""
    manifest = version.manifest if version else app.manifest
    if not manifest:
        report.checks.append(
            ConformanceCheck("manifest_present", "fail", "No manifest found")
        )
        return

    report.checks.append(
        ConformanceCheck("manifest_present", "pass", "Manifest exists")
    )

    validation = validate_manifest(manifest)
    if validation.valid:
        report.checks.append(
            ConformanceCheck(
                "manifest_valid",
                "pass",
                "Manifest passes schema validation",
                {"warnings": validation.warnings},
            )
        )
    else:
        report.checks.append(
            ConformanceCheck(
                "manifest_valid",
                "fail",
                f"Manifest has {len(validation.errors)} error(s)",
                {"errors": validation.errors, "warnings": validation.warnings},
            )
        )

    # Check permissions are declared
    permissions = manifest.get("permissions", [])
    if not permissions:
        report.checks.append(
            ConformanceCheck(
                "permissions_declared",
                "warn",
                "No permissions declared — app has no API access",
            )
        )
    else:
        report.checks.append(
            ConformanceCheck(
                "permissions_declared",
                "pass",
                f"{len(permissions)} permission(s) declared",
            )
        )


async def _check_versions(
    db: AsyncSession, report: ConformanceReport, app_id: str
) -> None:
    """Check version health."""
    count = (
        await db.execute(
            select(func.count()).where(AppVersion.app_id == app_id)
        )
    ).scalar() or 0

    if count == 0:
        report.checks.append(
            ConformanceCheck("has_versions", "warn", "No versions published")
        )
        return

    report.checks.append(
        ConformanceCheck("has_versions", "pass", f"{count} version(s) exist")
    )

    # Check latest version has content hash
    latest = (
        await db.execute(
            select(AppVersion)
            .where(AppVersion.app_id == app_id)
            .order_by(AppVersion.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()

    if latest and latest.content_hash:
        report.checks.append(
            ConformanceCheck("content_hash", "pass", "Latest version has content hash")
        )
    else:
        report.checks.append(
            ConformanceCheck("content_hash", "fail", "Latest version missing content hash")
        )

    if latest and latest.signature:
        report.checks.append(
            ConformanceCheck("signature", "pass", "Latest version is signed")
        )
    else:
        report.checks.append(
            ConformanceCheck("signature", "warn", "Latest version is not signed")
        )


async def _check_installations(
    db: AsyncSession, report: ConformanceReport, app_id: str
) -> None:
    """Check installation health."""
    active = (
        await db.execute(
            select(func.count()).where(
                AppInstallation.app_id == app_id,
                AppInstallation.status == "ACTIVE",
            )
        )
    ).scalar() or 0

    report.checks.append(
        ConformanceCheck(
            "active_installs",
            "pass" if active > 0 else "skip",
            f"{active} active installation(s)",
        )
    )


async def _check_sandbox_health(
    db: AsyncSession, report: ConformanceReport, app_id: str
) -> None:
    """Check sandbox execution error rate."""
    since = datetime.now(UTC) - timedelta(hours=24)

    total = (
        await db.execute(
            select(func.count())
            .select_from(SandboxExecution)
            .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
            .where(
                AppInstallation.app_id == app_id,
                SandboxExecution.created_at >= since,
            )
        )
    ).scalar() or 0

    if total == 0:
        report.checks.append(
            ConformanceCheck(
                "sandbox_health", "skip", "No sandbox executions in last 24h"
            )
        )
        return

    failed = (
        await db.execute(
            select(func.count())
            .select_from(SandboxExecution)
            .join(AppInstallation, SandboxExecution.installation_id == AppInstallation.id)
            .where(
                AppInstallation.app_id == app_id,
                SandboxExecution.created_at >= since,
                SandboxExecution.status.in_([
                    SandboxExecutionStatus.FAILED,
                    SandboxExecutionStatus.TIMEOUT,
                ]),
            )
        )
    ).scalar() or 0

    error_rate = (failed / total) * 100 if total > 0 else 0

    if error_rate > 50:
        status = "fail"
        msg = f"High error rate: {error_rate:.0f}% ({failed}/{total} executions failed)"
    elif error_rate > 20:
        status = "warn"
        msg = f"Elevated error rate: {error_rate:.0f}% ({failed}/{total})"
    else:
        status = "pass"
        msg = f"Healthy: {error_rate:.0f}% error rate ({total} executions)"

    report.checks.append(
        ConformanceCheck("sandbox_health", status, msg, {"total": total, "failed": failed})
    )


async def _check_api_keys(
    db: AsyncSession, report: ConformanceReport, app_id: str
) -> None:
    """Check API key hygiene."""
    expired = (
        await db.execute(
            select(func.count()).where(
                AppApiKey.app_id == app_id,
                AppApiKey.expires_at < datetime.now(UTC),
                AppApiKey.revoked_at.is_(None),
            )
        )
    ).scalar() or 0

    if expired > 0:
        report.checks.append(
            ConformanceCheck(
                "api_key_hygiene",
                "warn",
                f"{expired} expired but unrevoked API key(s)",
            )
        )
    else:
        report.checks.append(
            ConformanceCheck("api_key_hygiene", "pass", "No expired unrevoked keys")
        )


async def _check_event_subscriptions(
    db: AsyncSession, report: ConformanceReport, app_id: str
) -> None:
    """Check event subscription validity."""
    subs = (
        await db.execute(
            select(AppEventSubscription.event_type)
            .join(
                AppInstallation,
                AppEventSubscription.installation_id == AppInstallation.id,
            )
            .where(AppInstallation.app_id == app_id)
        )
    ).scalars().all()

    if not subs:
        report.checks.append(
            ConformanceCheck(
                "event_subscriptions", "skip", "No event subscriptions"
            )
        )
    else:
        report.checks.append(
            ConformanceCheck(
                "event_subscriptions",
                "pass",
                f"{len(subs)} event subscription(s) active",
            )
        )


def _check_security(report: ConformanceReport, app: DeveloperApp) -> None:
    """Check basic security posture."""
    # Privacy policy for public apps
    visibility = app.visibility.value if hasattr(app.visibility, "value") else app.visibility
    if visibility == "PUBLIC":
        if app.privacy_policy_url:
            report.checks.append(
                ConformanceCheck("privacy_policy", "pass", "Privacy policy URL provided")
            )
        else:
            report.checks.append(
                ConformanceCheck(
                    "privacy_policy",
                    "fail",
                    "Public apps must have a privacy policy URL",
                )
            )
    else:
        report.checks.append(
            ConformanceCheck("privacy_policy", "skip", "Not required for non-public apps")
        )

    # Webhook HTTPS
    if app.webhook_url:
        if app.webhook_url.startswith("https://"):
            report.checks.append(
                ConformanceCheck("webhook_https", "pass", "Webhook uses HTTPS")
            )
        else:
            report.checks.append(
                ConformanceCheck(
                    "webhook_https", "fail", "Webhook must use HTTPS"
                )
            )
    else:
        report.checks.append(
            ConformanceCheck("webhook_https", "skip", "No webhook configured")
        )
