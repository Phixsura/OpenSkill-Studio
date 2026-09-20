"""Data retention policy enforcement and consent audit trail (N20).

Policies:
  notifications    — delete after 90 days
  activity_log     — anonymize after 365 days (set user_id to 'anonymized')
  expired_snapshots — revoke when past expires_at
  closed_applications — anonymize after 730 days (2 years)

Evidence is retained indefinitely (audit requirement) but can be
anonymized on explicit user deletion request (handled by GDPR service).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.activity import TalentActivityLog
from app.talent.models.consent_log import ConsentLog
from app.talent.models.notification import TalentNotification
from app.talent.models.passport import PassportSnapshot

RETENTION_POLICIES: dict[str, dict] = {
    "notifications": {"retention_days": 90, "action": "delete"},
    "activity_log": {"retention_days": 365, "action": "anonymize"},
    "expired_snapshots": {"retention_days": 0, "action": "revoke"},
    "closed_applications": {"retention_days": 730, "action": "anonymize"},
}


@dataclass(frozen=True, slots=True)
class RetentionReport:
    """Result of a retention policy enforcement run."""

    policy: str
    records_affected: int
    action: str
    cutoff_date: datetime


# NOTE: Add cleanup for stale draft applications (>30 days) and expired snapshots

class DataRetentionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def preview_retention(self) -> list[RetentionReport]:
        """Preview what would be affected by retention policies.

        Does NOT modify data — preview only.
        """
        now = datetime.now(UTC)
        reports: list[RetentionReport] = []

        # Notifications older than 90 days
        notif_cutoff = now - timedelta(days=RETENTION_POLICIES["notifications"]["retention_days"])
        notif_q = select(TalentNotification).where(TalentNotification.created_at < notif_cutoff)
        notif_result = await self.db.execute(notif_q)
        notif_count = len(notif_result.scalars().all())
        reports.append(
            RetentionReport(
                policy="notifications",
                records_affected=notif_count,
                action="delete",
                cutoff_date=notif_cutoff,
            )
        )

        # Activity log older than 1 year (non-anonymized)
        activity_cutoff = now - timedelta(days=RETENTION_POLICIES["activity_log"]["retention_days"])
        activity_q = select(TalentActivityLog).where(
            TalentActivityLog.created_at < activity_cutoff,
            TalentActivityLog.user_id != "anonymized",
        )
        activity_result = await self.db.execute(activity_q)
        activity_count = len(activity_result.scalars().all())
        reports.append(
            RetentionReport(
                policy="activity_log",
                records_affected=activity_count,
                action="anonymize",
                cutoff_date=activity_cutoff,
            )
        )

        # Expired snapshots
        snapshot_q = select(PassportSnapshot).where(
            PassportSnapshot.expires_at.isnot(None),
            PassportSnapshot.expires_at < now,
            PassportSnapshot.status == "active",
        )
        snapshot_result = await self.db.execute(snapshot_q)
        snapshot_count = len(snapshot_result.scalars().all())
        reports.append(
            RetentionReport(
                policy="expired_snapshots",
                records_affected=snapshot_count,
                action="revoke",
                cutoff_date=now,
            )
        )

        return reports

    async def enforce_retention(self) -> list[RetentionReport]:
        """Enforce all retention policies. Modifies data."""
        now = datetime.now(UTC)
        reports: list[RetentionReport] = []

        # 1. Delete old notifications
        notif_cutoff = now - timedelta(days=RETENTION_POLICIES["notifications"]["retention_days"])
        from sqlalchemy import delete as sql_delete

        notif_del = sql_delete(TalentNotification).where(
            TalentNotification.created_at < notif_cutoff
        )
        notif_result = await self.db.execute(notif_del)
        reports.append(
            RetentionReport(
                policy="notifications",
                records_affected=notif_result.rowcount or 0,
                action="delete",
                cutoff_date=notif_cutoff,
            )
        )

        # 2. Anonymize old activity logs
        activity_cutoff = now - timedelta(days=RETENTION_POLICIES["activity_log"]["retention_days"])
        activity_upd = (
            update(TalentActivityLog)
            .where(
                TalentActivityLog.created_at < activity_cutoff,
                TalentActivityLog.user_id != "anonymized",
            )
            .values(user_id="anonymized")
        )
        activity_result = await self.db.execute(activity_upd)
        reports.append(
            RetentionReport(
                policy="activity_log",
                records_affected=activity_result.rowcount or 0,
                action="anonymize",
                cutoff_date=activity_cutoff,
            )
        )

        # 3. Revoke expired snapshots
        snapshot_upd = (
            update(PassportSnapshot)
            .where(
                PassportSnapshot.expires_at.isnot(None),
                PassportSnapshot.expires_at < now,
                PassportSnapshot.status == "active",
            )
            .values(status="revoked")
        )
        snapshot_result = await self.db.execute(snapshot_upd)
        reports.append(
            RetentionReport(
                policy="expired_snapshots",
                records_affected=snapshot_result.rowcount or 0,
                action="revoke",
                cutoff_date=now,
            )
        )

        await self.db.flush()
        return reports

    async def get_consent_audit_trail(
        self,
        user_id: str,
        *,
        consent_type: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Get complete consent change history for a user."""
        q = select(ConsentLog).where(ConsentLog.user_id == user_id)
        if consent_type:
            q = q.where(ConsentLog.consent_type == consent_type)
        q = q.order_by(ConsentLog.created_at.desc()).limit(limit)
        result = await self.db.execute(q)

        return [
            {
                "id": log.id,
                "consent_type": log.consent_type,
                "action": log.action,
                "details": log.details,
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in result.scalars().all()
        ]

    async def log_consent(
        self,
        *,
        user_id: str,
        consent_type: str,
        action: str,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> ConsentLog:
        """Record a consent change in the audit log."""
        log = ConsentLog(
            user_id=user_id,
            consent_type=consent_type,
            action=action,
            details=details or {},
            ip_address=ip_address,
        )
        self.db.add(log)
        await self.db.flush()
        return log
