"""Passport service — user-owned talent passport with privacy controls (ADR-015 D4).

Private by default. Users control sharing scope and field visibility.
Snapshots are immutable with SHA-256 tamper detection.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.passport import (
    PASSPORT_SHAREABLE_FIELDS,
    PassportSnapshot,
    SkillPassport,
)
from app.talent.services.scoring import compute_capability_profile


class PassportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_passport(self, user_id: str) -> SkillPassport:
        """Lazy-init: create a passport on first access."""
        passport = await self.db.get(SkillPassport, user_id)
        if passport:
            return passport

        passport = SkillPassport(user_id=user_id)
        self.db.add(passport)
        await self.db.flush()
        return passport

    async def update_passport(
        self,
        user_id: str,
        *,
        default_visibility: str | None = None,
        visible_fields: list[str] | None = None,
        preferred_opportunity_types: list[str] | None = None,
        availability_status: str | None = None,
        availability_note: str | None = None,
        discoverable: bool | None = None,
        discoverable_to: list[str] | None = ...,  # type: ignore[assignment]
    ) -> SkillPassport:
        """Update passport settings."""
        passport = await self.get_or_create_passport(user_id)

        if default_visibility is not None:
            if default_visibility not in ("private", "organization_only", "share_link", "public_subset"):
                raise ValueError(f"Invalid visibility: {default_visibility}")
            passport.default_visibility = default_visibility

        if visible_fields is not None:
            invalid = set(visible_fields) - PASSPORT_SHAREABLE_FIELDS
            if invalid:
                raise ValueError(f"Invalid visible_fields: {invalid}")
            passport.visible_fields = visible_fields

        if preferred_opportunity_types is not None:
            passport.preferred_opportunity_types = preferred_opportunity_types

        if availability_status is not None:
            passport.availability_status = availability_status

        if availability_note is not None:
            passport.availability_note = availability_note

        if discoverable is not None:
            passport.discoverable = discoverable

        if discoverable_to is not ...:
            passport.discoverable_to = discoverable_to

        await self.db.flush()
        return passport

    async def get_visible_passport(
        self,
        user_id: str,
        *,
        requesting_user_id: str | None = None,
        requesting_org_id: str | None = None,
    ) -> dict | None:
        """Return passport summary respecting privacy settings.

        Returns None if the passport is private and requestor has no access.
        """
        passport = await self.db.get(SkillPassport, user_id)
        if not passport:
            return None

        # Owner always sees everything
        if requesting_user_id == user_id:
            return await self._build_full_passport(user_id, passport)

        # Check visibility
        if passport.default_visibility == "private":
            return None

        if passport.default_visibility == "organization_only" and not requesting_org_id:
            return None
            # Would need to check org membership — deferred to caller
            # For now, trust the caller's org context

        # Build filtered passport based on visible_fields
        return await self._build_filtered_passport(user_id, passport)

    async def _build_full_passport(self, user_id: str, passport: SkillPassport) -> dict:
        """Build complete passport for the owner."""
        profile = await compute_capability_profile(self.db, user_id)

        return {
            "user_id": user_id,
            "default_visibility": passport.default_visibility,
            "discoverable": passport.discoverable,
            "availability_status": passport.availability_status,
            "availability_note": passport.availability_note,
            "preferred_opportunity_types": passport.preferred_opportunity_types,
            "visible_fields": passport.visible_fields,
            "capabilities": [
                {
                    "capability_id": s.capability_id,
                    "capability_name": s.capability_name,
                    "level": s.level,
                    "level_label": s.level_label,
                    "score": s.score,
                    "confidence": s.confidence,
                    "evidence_count": s.evidence_count,
                    "last_verified_at": s.last_verified_at.isoformat() if s.last_verified_at else None,
                    "verification_mix": s.verification_mix,
                }
                for s in profile
            ],
        }

    async def _build_filtered_passport(self, user_id: str, passport: SkillPassport) -> dict:
        """Build passport filtered by visible_fields."""
        result: dict = {"user_id": user_id}
        fields = set(passport.visible_fields or [])

        if "capabilities" in fields:
            profile = await compute_capability_profile(self.db, user_id)
            result["capabilities"] = [
                {
                    "capability_id": s.capability_id,
                    "capability_name": s.capability_name,
                    "level": s.level,
                    "level_label": s.level_label,
                    "score": s.score,
                    "evidence_count": s.evidence_count,
                }
                for s in profile
            ]

        if "availability" in fields:
            result["availability_status"] = passport.availability_status
            result["preferred_opportunity_types"] = passport.preferred_opportunity_types

        # Other fields (credentials, projects, portfolio, etc.) loaded on demand
        # and added only if in visible_fields. Deferred to specific sub-services.

        return result

    async def create_snapshot(
        self,
        user_id: str,
        *,
        included_fields: list[str] | None = None,
        expires_at: datetime | None = None,
    ) -> PassportSnapshot:
        """Create an immutable share snapshot."""
        passport = await self.get_or_create_passport(user_id)

        # Build the payload based on included_fields (or all visible).
        # Do NOT mutate passport.visible_fields — snapshot creation is read-only
        # on the passport row; it only writes the snapshot row.
        fields = included_fields or list(passport.visible_fields or PASSPORT_SHAREABLE_FIELDS)

        # Build full payload for snapshot
        full = await self._build_full_passport(user_id, passport)
        # Filter to included fields
        payload: dict = {"user_id": user_id, "snapshot_at": datetime.now(UTC).isoformat()}
        for field in fields:
            if field in full:
                payload[field] = full[field]

        # Canonical JSON for checksum
        canonical = json.dumps(payload, sort_keys=True, default=str)
        checksum = hashlib.sha256(canonical.encode()).hexdigest()

        snapshot = PassportSnapshot(
            user_id=user_id,
            share_token=secrets.token_urlsafe(48),
            payload=payload,
            checksum=checksum,
            included_fields=fields,
            expires_at=expires_at,
        )
        self.db.add(snapshot)
        await self.db.flush()
        return snapshot

    async def revoke_snapshot(self, snapshot_id: str, user_id: str) -> PassportSnapshot | None:
        """Revoke a snapshot. Returns None if not found or not owned."""
        snapshot = await self.db.get(PassportSnapshot, snapshot_id)
        if not snapshot or snapshot.user_id != user_id:
            return None
        if snapshot.status != "active":
            return None

        snapshot.status = "revoked"
        await self.db.flush()
        return snapshot

    async def verify_snapshot(self, share_token: str) -> dict | None:
        """Public verification: return frozen payload + checksum.

        Returns None for revoked/expired snapshots.
        """
        result = await self.db.execute(
            select(PassportSnapshot).where(PassportSnapshot.share_token == share_token)
        )
        snapshot = result.scalar_one_or_none()
        if not snapshot:
            return None

        if snapshot.status == "revoked":
            return {"status": "revoked", "revoked": True}

        now = datetime.now(UTC)
        if snapshot.expires_at and snapshot.expires_at < now:
            return {"status": "expired", "expired": True}

        return {
            "status": "active",
            "payload": snapshot.payload,
            "checksum": snapshot.checksum,
            "issued_at": snapshot.issued_at.isoformat() if snapshot.issued_at else None,
            "expires_at": snapshot.expires_at.isoformat() if snapshot.expires_at else None,
        }
