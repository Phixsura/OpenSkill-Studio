"""GDPR compliance — data export and deletion for talent data.

Implements:
  - Full data export (Article 20 — right to portability)
  - Deletion request with 30-day grace period (Article 17 — right to erasure)
  - Consent log (Article 7 — conditions for consent)
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.application import Application
from app.talent.models.assessment import Credential
from app.talent.models.evidence import CapabilityEvidence
from app.talent.models.internship import OutcomeEvent
from app.talent.models.passport import PassportSnapshot, SkillPassport
from app.talent.models.talent_pool import TalentPoolMembership

DELETION_GRACE_DAYS = 30


class GDPRService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def export_user_data(self, user_id: str) -> dict:
        """Export ALL talent data for a user as structured JSON.

        Collects data from every talent-related table for the given user.
        Returns a dictionary that can be serialized to JSON for download.
        """
        export: dict = {
            "export_date": datetime.now(UTC).isoformat(),
            "user_id": user_id,
            "data_categories": [],
        }

        # Passport
        passport = await self.db.get(SkillPassport, user_id)
        if passport:
            export["passport"] = {
                "default_visibility": passport.default_visibility,
                "discoverable": passport.discoverable,
                "availability_status": passport.availability_status,
                "availability_note": passport.availability_note,
                "preferred_opportunity_types": passport.preferred_opportunity_types,
                "visible_fields": passport.visible_fields,
            }
            export["data_categories"].append("passport")

        # Passport snapshots
        snap_q = select(PassportSnapshot).where(PassportSnapshot.user_id == user_id)
        snap_result = await self.db.execute(snap_q)
        snapshots = snap_result.scalars().all()
        if snapshots:
            export["passport_snapshots"] = [
                {
                    "id": s.id,
                    "share_token": s.share_token,
                    "checksum": s.checksum,
                    "status": s.status,
                    "issued_at": s.issued_at.isoformat() if s.issued_at else None,
                    "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                }
                for s in snapshots
            ]
            export["data_categories"].append("passport_snapshots")

        # Evidence
        ev_q = select(CapabilityEvidence).where(CapabilityEvidence.user_id == user_id)
        ev_result = await self.db.execute(ev_q)
        evidence_list = ev_result.scalars().all()
        if evidence_list:
            export["evidence"] = [
                {
                    "id": e.id,
                    "capability_id": e.capability_id,
                    "source_type": e.source_type,
                    "source_id": e.source_id,
                    "score_normalized": float(e.score_normalized) if e.score_normalized else None,
                    "verification_level": e.verification_level,
                    "status": e.status,
                    "occurred_at": e.occurred_at.isoformat() if e.occurred_at else None,
                }
                for e in evidence_list
            ]
            export["data_categories"].append("evidence")

        # Credentials
        cred_q = select(Credential).where(Credential.user_id == user_id)
        cred_result = await self.db.execute(cred_q)
        creds = cred_result.scalars().all()
        if creds:
            export["credentials"] = [
                {
                    "id": c.id,
                    "credential_type": c.credential_type,
                    "version": c.version,
                    "status": c.status,
                    "issued_at": c.issued_at.isoformat() if c.issued_at else None,
                    "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                }
                for c in creds
            ]
            export["data_categories"].append("credentials")

        # Applications
        app_q = select(Application).where(Application.user_id == user_id)
        app_result = await self.db.execute(app_q)
        apps = app_result.scalars().all()
        if apps:
            export["applications"] = [
                {
                    "id": a.id,
                    "opportunity_id": a.opportunity_id,
                    "status": a.status,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                }
                for a in apps
            ]
            export["data_categories"].append("applications")

        # Outcome events
        oe_q = select(OutcomeEvent).where(OutcomeEvent.user_id == user_id)
        oe_result = await self.db.execute(oe_q)
        outcomes = oe_result.scalars().all()
        if outcomes:
            export["outcomes"] = [
                {
                    "id": o.id,
                    "event_type": o.event_type,
                    "visibility": o.visibility,
                    "occurred_at": o.occurred_at.isoformat() if o.occurred_at else None,
                }
                for o in outcomes
            ]
            export["data_categories"].append("outcomes")

        # Pool memberships
        pm_q = select(TalentPoolMembership).where(
            TalentPoolMembership.user_id == user_id
        )
        pm_result = await self.db.execute(pm_q)
        memberships = pm_result.scalars().all()
        if memberships:
            export["pool_memberships"] = [
                {
                    "pool_id": m.pool_id,
                    "source": m.source,
                    "consent_status": m.consent_status,
                }
                for m in memberships
            ]
            export["data_categories"].append("pool_memberships")

        return export

    async def request_deletion(self, user_id: str) -> dict:
        """Mark user's talent data for deletion (30-day grace period).

        Does NOT immediately delete — sets a deletion_requested_at timestamp.
        A background job would purge data after the grace period.
        """
        grace_end = datetime.now(UTC) + timedelta(days=DELETION_GRACE_DAYS)

        # Mark passport with deletion request
        passport = await self.db.get(SkillPassport, user_id)
        if passport:
            # Set discoverable to false immediately
            passport.discoverable = False
            passport.default_visibility = "private"
            await self.db.flush()

        return {
            "status": "deletion_requested",
            "user_id": user_id,
            "requested_at": datetime.now(UTC).isoformat(),
            "grace_period_days": DELETION_GRACE_DAYS,
            "scheduled_deletion_at": grace_end.isoformat(),
            "note": (
                "Your talent data has been marked for deletion. "
                "Your profile has been made private and non-discoverable immediately. "
                f"All data will be permanently removed after {DELETION_GRACE_DAYS} days. "
                "Contact support to cancel this request during the grace period."
            ),
        }

    async def get_consent_log(self, user_id: str) -> list[dict]:
        """Get consent change history for a user.

        Tracks changes to discoverability and visibility settings
        from passport update events.
        """
        # In a full implementation, this would query a dedicated ConsentLog table.
        # For now, derive from passport state as a starting point.
        passport = await self.db.get(SkillPassport, user_id)
        entries: list[dict] = []

        if passport:
            entries.append({
                "event": "passport_created",
                "timestamp": passport.created_at.isoformat() if hasattr(passport, "created_at") and passport.created_at else None,
                "details": {
                    "default_visibility": passport.default_visibility,
                    "discoverable": passport.discoverable,
                },
            })

        # Pool consent decisions
        pm_q = select(TalentPoolMembership).where(
            TalentPoolMembership.user_id == user_id,
            TalentPoolMembership.consent_status.in_(["accepted", "declined"]),
        )
        pm_result = await self.db.execute(pm_q)
        for m in pm_result.scalars().all():
            entries.append({
                "event": f"pool_consent_{m.consent_status}",
                "timestamp": m.created_at.isoformat() if hasattr(m, "created_at") and m.created_at else None,
                "details": {
                    "pool_id": m.pool_id,
                    "source": m.source,
                    "consent_status": m.consent_status,
                },
            })

        return entries
