"""Credential pathway service — stackable credentials (N2).

Manages credential pathways: ordered sets of prerequisite credentials
that unlock a higher-level pathway credential. Supports auto-issuance
when all prerequisites (or N of M) are met.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.assessment import Credential
from app.talent.models.credential_pathway import CredentialPathway


class CredentialPathwayService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pathway(
        self,
        *,
        org_id: str,
        name: str,
        pathway_credential_type: str,
        prerequisite_credential_types: list[str],
        prerequisite_count: int | None = None,
        description: str | None = None,
        auto_issue: bool = True,
        created_by: str | None = None,
    ) -> CredentialPathway:
        if len(prerequisite_credential_types) < 2:
            raise ValueError("A pathway must have at least 2 prerequisite credential types")

        # Default: require all prerequisites
        if prerequisite_count is None:
            prerequisite_count = len(prerequisite_credential_types)

        if prerequisite_count > len(prerequisite_credential_types):
            raise ValueError(
                f"prerequisite_count ({prerequisite_count}) cannot exceed "
                f"number of prerequisites ({len(prerequisite_credential_types)})"
            )
        if prerequisite_count < 1:
            raise ValueError("prerequisite_count must be at least 1")

        pathway = CredentialPathway(
            org_id=org_id,
            name=name,
            description=description,
            pathway_credential_type=pathway_credential_type,
            prerequisite_credential_types=prerequisite_credential_types,
            prerequisite_count=prerequisite_count,
            auto_issue=auto_issue,
            created_by=created_by,
        )
        self.db.add(pathway)
        await self.db.flush()
        return pathway

    async def get_pathway(self, pathway_id: str) -> CredentialPathway | None:
        """Execute get pathway."""
        return await self.db.get(CredentialPathway, pathway_id)

    async def list_pathways(
        self,
        org_id: str,
        *,
        status: str = "active",
        cursor: str | None = None,
        limit: int = 50,
    ) -> tuple[list[CredentialPathway], bool]:
        q = select(CredentialPathway).where(
            CredentialPathway.org_id == org_id,
            CredentialPathway.status == status,
        )
        if cursor:
            q = q.where(CredentialPathway.id < cursor)
        q = q.order_by(CredentialPathway.created_at.desc()).limit(limit + 1)
        result = await self.db.execute(q)
        items = list(result.scalars().all())
        has_more = len(items) > limit
        if has_more:
            items = items[:limit]
        return items, has_more

    async def update_pathway(
        self, pathway_id: str, **fields: object
    ) -> CredentialPathway | None:
        pathway = await self.db.get(CredentialPathway, pathway_id)
        if not pathway:
            return None

        # Validate prerequisite_count if being updated
        new_count = fields.get("prerequisite_count")
        if new_count is not None:
            max_prereqs = len(pathway.prerequisite_credential_types)
            if int(new_count) > max_prereqs:
                raise ValueError(
                    f"prerequisite_count ({new_count}) cannot exceed "
                    f"number of prerequisites ({max_prereqs})"
                )

        for key, value in fields.items():
            if hasattr(pathway, key) and value is not None:
                setattr(pathway, key, value)
        await self.db.flush()
        return pathway

    async def check_pathway_completion(
        self, user_id: str, pathway_id: str
    ) -> dict:
        """Check if a user has completed a pathway's prerequisites."""
        pathway = await self.db.get(CredentialPathway, pathway_id)
        if not pathway:
            return {
                "completed": False,
                "pathway_id": pathway_id,
                "pathway_name": "",
                "target_credential_type": "",
                "required_count": 0,
                "earned_count": 0,
                "earned_credentials": [],
                "missing_credential_types": [],
            }

        prereq_types = set(pathway.prerequisite_credential_types)

        # Find user's active credentials matching prerequisite types
        q = select(Credential).where(
            Credential.user_id == user_id,
            Credential.status == "active",
            Credential.credential_type.in_(prereq_types),
        )
        result = await self.db.execute(q)
        earned = result.scalars().all()

        earned_types = {c.credential_type for c in earned}
        earned_list = [
            {
                "credential_type": c.credential_type,
                "issued_at": c.issued_at.isoformat() if c.issued_at else None,
            }
            for c in earned
        ]
        missing = sorted(prereq_types - earned_types)

        return {
            "completed": len(earned_types) >= pathway.prerequisite_count,
            "pathway_id": pathway.id,
            "pathway_name": pathway.name,
            "target_credential_type": pathway.pathway_credential_type,
            "required_count": pathway.prerequisite_count,
            "earned_count": len(earned_types),
            "earned_credentials": earned_list,
            "missing_credential_types": missing,
        }

    async def check_and_auto_issue(
        self, user_id: str, pathway_id: str
    ) -> Credential | None:
        """Check completion and auto-issue the pathway credential if met.

        Returns the issued Credential or None if not yet complete or
        already issued or auto_issue is disabled.
        """
        pathway = await self.db.get(CredentialPathway, pathway_id)
        if not pathway or not pathway.auto_issue:
            return None

        progress = await self.check_pathway_completion(user_id, pathway_id)
        if not progress["completed"]:
            return None

        # Check if user already has the pathway credential
        existing_q = select(Credential).where(
            Credential.user_id == user_id,
            Credential.credential_type == pathway.pathway_credential_type,
            Credential.status == "active",
        )
        existing = (await self.db.execute(existing_q)).scalar_one_or_none()
        if existing:
            return None  # Already issued

        # Issue the pathway credential
        credential = Credential(
            credential_type=pathway.pathway_credential_type,
            version=1,
            issuer_org_id=pathway.org_id,
            user_id=user_id,
            capabilities=[],
            evidence_references=[
                {"type": "pathway", "pathway_id": pathway.id}
            ] + [
                {"type": "prerequisite", "credential_type": ec["credential_type"]}
                for ec in progress["earned_credentials"]
            ],
            status="active",
            issued_at=datetime.now(UTC),
        )
        self.db.add(credential)
        await self.db.flush()
        return credential

    async def list_user_pathway_progress(
        self, user_id: str, *, org_id: str | None = None
    ) -> list[dict]:
        """List all active pathways with user's progress toward each."""
        q = select(CredentialPathway).where(CredentialPathway.status == "active")
        if org_id:
            q = q.where(CredentialPathway.org_id == org_id)
        q = q.order_by(CredentialPathway.name)

        result = await self.db.execute(q)
        pathways = result.scalars().all()

        progress_list = []
        for pathway in pathways:
            progress = await self.check_pathway_completion(user_id, pathway.id)
            progress_list.append(progress)

        return progress_list
