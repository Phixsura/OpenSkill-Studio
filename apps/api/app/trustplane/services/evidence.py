"""Assurance Case & Evidence Graph service (ADR-017 Part C).

Module-level functions, db: AsyncSession first arg, no db.commit().
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.evidence import (
    AssuranceCase,
    ClaimStatus,
    EvidenceItem,
    EvidenceLink,
    EvidenceStatus,
    EvidenceType,
    LinkRelation,
)
from app.trustplane.models.inventory import AISystem
from app.trustplane.services.audit import record_trust_audit
from app.trustplane.services.inventory import SystemNotFoundError

# ── Errors ───────────────────────────────────────────────────────────


class CaseNotFoundError(AppError):
    def __init__(self):
        super().__init__("CASE_NOT_FOUND", "Assurance case not found", 404)


class EvidenceNotFoundError(AppError):
    def __init__(self):
        super().__init__("EVIDENCE_NOT_FOUND", "Evidence item not found", 404)


class LinkNotFoundError(AppError):
    def __init__(self):
        super().__init__("LINK_NOT_FOUND", "Evidence link not found", 404)


class DuplicateLinkError(AppError):
    def __init__(self):
        super().__init__("DUPLICATE_LINK", "This evidence is already linked to this case", 409)


# ── Assurance Case CRUD ──────────────────────────────────────────────


async def create_case(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    system_id: str,
    title: str,
    claim: str,
    description: str | None = None,
) -> AssuranceCase:
    # Validate system belongs to org
    result = await db.execute(
        select(AISystem).where(AISystem.id == system_id, AISystem.org_id == org_id)
    )
    if result.scalar_one_or_none() is None:
        raise SystemNotFoundError()

    case = AssuranceCase(
        org_id=org_id,
        system_id=system_id,
        title=title,
        claim=claim,
        description=description,
        status=ClaimStatus.DRAFT,
        owner_user_id=user_id,
    )
    db.add(case)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="case.created",
        target_type="assurance_case",
        target_id=case.id,
        after={"title": title, "system_id": system_id},
    )
    return case


async def get_case(db: AsyncSession, case_id: str, org_id: str) -> AssuranceCase:
    result = await db.execute(
        select(AssuranceCase).where(AssuranceCase.id == case_id, AssuranceCase.org_id == org_id)
    )
    case = result.scalar_one_or_none()
    if case is None:
        raise CaseNotFoundError()
    return case


async def list_cases(
    db: AsyncSession,
    org_id: str,
    *,
    system_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AssuranceCase], int]:
    base = select(AssuranceCase).where(AssuranceCase.org_id == org_id)
    count_base = select(func.count()).select_from(AssuranceCase).where(AssuranceCase.org_id == org_id)

    if system_id:
        base = base.where(AssuranceCase.system_id == system_id)
        count_base = count_base.where(AssuranceCase.system_id == system_id)
    if status:
        base = base.where(AssuranceCase.status == status)
        count_base = count_base.where(AssuranceCase.status == status)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(AssuranceCase.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def update_case(
    db: AsyncSession,
    case_id: str,
    org_id: str,
    user_id: str,
    **fields,
) -> AssuranceCase:
    case = await get_case(db, case_id, org_id)
    before = {}
    after = {}

    for key, value in fields.items():
        if value is not None and hasattr(case, key):
            old = getattr(case, key)
            if isinstance(old, ClaimStatus):
                old = old.value
            before[key] = old
            setattr(case, key, value)
            after[key] = value

    await db.flush()
    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="case.updated",
        target_type="assurance_case",
        target_id=case_id,
        before=before,
        after=after,
    )
    return case


async def change_case_status(
    db: AsyncSession,
    case_id: str,
    org_id: str,
    user_id: str,
    new_status: str,
) -> AssuranceCase:
    case = await get_case(db, case_id, org_id)
    old = case.status.value
    case.status = ClaimStatus(new_status)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="case.status_changed",
        target_type="assurance_case",
        target_id=case_id,
        before={"status": old},
        after={"status": new_status},
    )
    return case


# ── Evidence Item CRUD ───────────────────────────────────────────────


async def create_evidence(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    title: str,
    evidence_type: str,
    description: str | None = None,
    source_type: str | None = None,
    source_id: str | None = None,
    source_version: str | None = None,
    scope: str | None = None,
    expires_at: str | None = None,
    revalidation_rule: str | None = None,
    content: dict | None = None,
    content_hash: str | None = None,
) -> EvidenceItem:
    from datetime import datetime

    item = EvidenceItem(
        org_id=org_id,
        title=title,
        evidence_type=EvidenceType(evidence_type),
        description=description,
        status=EvidenceStatus.DRAFT,
        source_type=source_type,
        source_id=source_id,
        source_version=source_version,
        scope=scope,
        expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        revalidation_rule=revalidation_rule,
        content=content,
        content_hash=content_hash,
        collected_by=user_id,
    )
    db.add(item)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="evidence.created",
        target_type="evidence_item",
        target_id=item.id,
        after={"title": title, "evidence_type": evidence_type},
    )
    return item


async def get_evidence(db: AsyncSession, evidence_id: str, org_id: str) -> EvidenceItem:
    result = await db.execute(
        select(EvidenceItem).where(EvidenceItem.id == evidence_id, EvidenceItem.org_id == org_id)
    )
    item = result.scalar_one_or_none()
    if item is None:
        raise EvidenceNotFoundError()
    return item


async def list_evidence(
    db: AsyncSession,
    org_id: str,
    *,
    evidence_type: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[EvidenceItem], int]:
    base = select(EvidenceItem).where(EvidenceItem.org_id == org_id)
    count_base = select(func.count()).select_from(EvidenceItem).where(EvidenceItem.org_id == org_id)

    if evidence_type:
        base = base.where(EvidenceItem.evidence_type == evidence_type)
        count_base = count_base.where(EvidenceItem.evidence_type == evidence_type)
    if status:
        base = base.where(EvidenceItem.status == status)
        count_base = count_base.where(EvidenceItem.status == status)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(EvidenceItem.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def change_evidence_status(
    db: AsyncSession,
    evidence_id: str,
    org_id: str,
    user_id: str,
    new_status: str,
) -> EvidenceItem:
    item = await get_evidence(db, evidence_id, org_id)
    old = item.status.value
    item.status = EvidenceStatus(new_status)
    if new_status == "superseded":
        item.version += 1
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="evidence.status_changed",
        target_type="evidence_item",
        target_id=evidence_id,
        before={"status": old},
        after={"status": new_status},
    )
    return item


# ── Evidence Linking ─────────────────────────────────────────────────


async def link_evidence(
    db: AsyncSession,
    case_id: str,
    evidence_id: str,
    org_id: str,
    user_id: str,
    *,
    relation: str = "supports",
    notes: str | None = None,
) -> EvidenceLink:
    # Validate both belong to org
    await get_case(db, case_id, org_id)
    await get_evidence(db, evidence_id, org_id)

    # Check for duplicate
    existing = await db.execute(
        select(EvidenceLink.id).where(
            EvidenceLink.case_id == case_id,
            EvidenceLink.evidence_id == evidence_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise DuplicateLinkError()

    link = EvidenceLink(
        case_id=case_id,
        evidence_id=evidence_id,
        relation=LinkRelation(relation),
        notes=notes,
        linked_by=user_id,
    )
    db.add(link)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="evidence.linked",
        target_type="evidence_link",
        target_id=link.id,
        after={"case_id": case_id, "evidence_id": evidence_id, "relation": relation},
    )
    return link


async def unlink_evidence(
    db: AsyncSession,
    link_id: str,
    org_id: str,
    user_id: str,
) -> None:
    result = await db.execute(select(EvidenceLink).where(EvidenceLink.id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise LinkNotFoundError()

    # Validate case belongs to org
    await get_case(db, link.case_id, org_id)

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="evidence.unlinked",
        target_type="evidence_link",
        target_id=link_id,
        before={"case_id": link.case_id, "evidence_id": link.evidence_id},
    )
    await db.delete(link)
    await db.flush()


async def list_case_evidence(
    db: AsyncSession,
    case_id: str,
    org_id: str,
) -> list[dict]:
    """Return evidence items linked to a case with their relation."""
    await get_case(db, case_id, org_id)

    result = await db.execute(
        select(EvidenceLink, EvidenceItem)
        .join(EvidenceItem, EvidenceLink.evidence_id == EvidenceItem.id)
        .where(EvidenceLink.case_id == case_id)
        .order_by(EvidenceLink.created_at)
    )
    rows = []
    for link, item in result.all():
        rows.append(
            {
                "link_id": link.id,
                "relation": link.relation.value,
                "notes": link.notes,
                "evidence": item,
            }
        )
    return rows
